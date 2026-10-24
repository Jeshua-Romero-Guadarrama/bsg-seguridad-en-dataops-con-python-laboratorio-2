"""Pruebas de la línea de comandos de lab1.py y de comprobar_1a.py por subprocess."""
import json
import subprocess
import sys

from pruebas.conftest import RAIZ

LAB1 = str(RAIZ / 'lab1.py')
COMPROBAR = str(RAIZ / 'comprobar_1a.py')


def lanzar(entorno, variables, accion, rol, destino, entrada=None):
    """Ejecuta lab1.py con rutas en tmp_path y devuelve el proceso terminado."""
    comando = [
        sys.executable, LAB1, accion, '--rol', rol,
        '--entrada', str(entrada or entorno.entrada),
        '--referencia', str(entorno.referencia),
        '--destino', str(destino),
    ]
    return subprocess.run(comando, env=variables, cwd=entorno.base,
                          capture_output=True, text=True, encoding='utf-8')


class PruebaInterfazPermitida:
    """Las tres operaciones permitidas terminan con código 0."""

    def prueba_secuencia_permitida(self, entorno, entorno_proceso):
        """ejecutar, resumen y recuperar muestran lo esperado."""
        destino = entorno.salidas / 'lab1'
        r = lanzar(entorno, entorno_proceso, 'ejecutar', 'operador', destino)
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == 'Proceso terminado: 12 filas'

        r = lanzar(entorno, entorno_proceso, 'resumen', 'analista', destino)
        assert r.returncode == 0, r.stderr
        assert r.stdout.split() == [
            'ciudad,total_ventas', 'Merida,4000.00',
            'Puebla,2500.00', 'Villahermosa,4250.00',
        ]

        r = lanzar(entorno, entorno_proceso, 'recuperar', 'operador', destino)
        assert r.returncode == 0, r.stderr
        assert json.loads(r.stdout) == {
            'nombre_cliente': 'Cliente Prueba 001',
            'correo': 'cliente001@example.com',
        }


class PruebaInterfazBloqueos:
    """Los bloqueos terminan con código 1, BLOQUEADO y sin destino."""

    def prueba_ejecutar_como_analista(self, entorno, entorno_proceso):
        """El analista no puede ejecutar."""
        destino = entorno.salidas / 'denegada_analista'
        r = lanzar(entorno, entorno_proceso, 'ejecutar', 'analista', destino)
        assert r.returncode == 1
        assert r.stderr.startswith('BLOQUEADO')
        assert not destino.exists()

    def prueba_ejecutar_con_rol_desconocido(self, entorno, entorno_proceso):
        """Un rol desconocido no puede ejecutar."""
        destino = entorno.salidas / 'denegada_desconocido'
        r = lanzar(entorno, entorno_proceso, 'ejecutar', 'desconocido',
                   destino)
        assert r.returncode == 1
        assert 'BLOQUEADO: Rol desconocido' in r.stderr
        assert not destino.exists()

    def prueba_recuperar_como_auditor(self, entorno, entorno_proceso):
        """El auditor no recupera la muestra y no ve datos personales."""
        destino = entorno.salidas / 'lab1'
        assert lanzar(entorno, entorno_proceso, 'ejecutar', 'operador',
                      destino).returncode == 0
        r = lanzar(entorno, entorno_proceso, 'recuperar', 'auditor', destino)
        assert r.returncode == 1
        assert 'BLOQUEADO' in r.stderr
        assert '@' not in r.stdout + r.stderr

    def prueba_entrada_alterada(self, entorno, entorno_proceso):
        """La copia alterada se bloquea por integridad."""
        alterada = entorno.alterar_entrada()
        destino = entorno.salidas / 'alterada'
        r = lanzar(entorno, entorno_proceso, 'ejecutar', 'operador', destino,
                   entrada=alterada)
        assert r.returncode == 1
        assert r.stderr.strip() == 'BLOQUEADO: Integridad de entrada no valida'
        assert not destino.exists()

    def prueba_sin_clave(self, entorno, entorno_proceso):
        """Sin DATAOPS_KEY no se crea el destino."""
        entorno_proceso.pop('DATAOPS_KEY')
        destino = entorno.salidas / 'sin_clave'
        r = lanzar(entorno, entorno_proceso, 'ejecutar', 'operador', destino)
        assert r.returncode == 1
        assert r.stderr.strip() == 'BLOQUEADO: Falta DATAOPS_KEY en el entorno'
        assert not destino.exists()


class PruebaComprobador1A:
    """comprobar_1a.py con --base sobre un entorno temporal."""

    def prueba_cuatro_lineas(self, entorno, entorno_proceso):
        """Imprime True, True, False y la verificación final."""
        r = subprocess.run(
            [sys.executable, COMPROBAR, '--base', str(entorno.base)],
            env=entorno_proceso, capture_output=True, text=True,
            encoding='utf-8')
        assert r.returncode == 0, r.stderr
        assert r.stdout.splitlines() == [
            'Recuperacion coincidente: True',
            'Original coincide con referencia: True',
            'Copia alterada coincide con referencia: False',
            'Laboratorio 1A verificado',
        ]
        assert (entorno.base / 'datos' / 'pedidos_prueba_parte1.csv').exists()
