"""Comprobaciones de 1A; no contiene la solucion de los TODO.

Verifica con las funciones de lab1.py que un correo cifrado se recupera igual,
que el original coincide con la referencia confiable y que una copia con un
solo importe alterado deja de coincidir.

Uso:
    python comprobar_1a.py [--base CARPETA]

Sin --base se usa la carpeta del repositorio (comportamiento original). Con
--base se usan CARPETA/datos y CARPETA/referencia.sha256, lo que permite
comprobar un entorno temporal creado con PreparadorEntorno.
"""
import argparse
import sys
from pathlib import Path

import lab1


class ComprobadorLaboratorio1A:
    """Ejecuta las tres comprobaciones del tramo 1A sobre una carpeta base."""

    def __init__(self, base=None):
        """Define las rutas de datos y referencia.

        Argumentos:
            base: carpeta del entorno; por omisión, la del módulo lab1.
        """
        if base is None:
            self.base = lab1.BASE
            self.datos = lab1.DATOS
        else:
            self.base = Path(base)
            self.datos = self.base / 'datos'

    def comprobar(self):
        """Ejecuta las comprobaciones e imprime cada resultado en orden.

        Lanza:
            NotImplementedError: si algún TODO de lab1.py sigue pendiente.
            AssertionError: si alguna comprobación no da el valor esperado.
            ValueError: si falta DATAOPS_KEY en el entorno.
            OSError: si faltan la entrada o la referencia.
        """
        fernet = lab1.cargar_cifrador()
        correo = "cliente001@example.com"
        token = lab1.cifrar(correo, fernet)
        recuperado = lab1.descifrar(token, fernet) == correo
        print(f"Recuperacion coincidente: {recuperado}")
        assert recuperado, "El dato recuperado no coincide"

        entrada = self.datos / "pedidos.csv"
        referencia = (self.base / "referencia.sha256").read_text().strip()
        original = lab1.calcular_hash(entrada) == referencia
        print(f"Original coincide con referencia: {original}")
        assert original, "Revisar el original; no recalcular la referencia"

        copia = self.datos / "pedidos_prueba_parte1.csv"
        contenido = entrada.read_bytes()
        alterado = contenido.replace(b"1850.00", b"1851.00", 1)
        assert alterado != contenido, "No se encontro el importe de prueba"
        copia.write_bytes(alterado)
        coincide = lab1.calcular_hash(copia) == referencia
        print(f"Copia alterada coincide con referencia: {coincide}")
        assert not coincide, "La alteracion no fue detectada"
        print("Laboratorio 1A verificado")


def main(argv=None):
    """Interpreta --base y ejecuta el comprobador.

    Argumentos:
        argv: lista de argumentos; por omisión se usa sys.argv.
    """
    parser = argparse.ArgumentParser(description='Comprobaciones del tramo 1A')
    parser.add_argument('--base', type=Path, default=None,
                        help='carpeta base con datos/ y referencia.sha256')
    args = parser.parse_args(argv)
    ComprobadorLaboratorio1A(args.base).comprobar()


if __name__ == "__main__":
    try:
        main()
    except NotImplementedError as exc:
        sys.exit(f"PENDIENTE: {exc}")
    except (AssertionError, ValueError, OSError) as exc:
        sys.exit(f"REVISAR: {exc}")
