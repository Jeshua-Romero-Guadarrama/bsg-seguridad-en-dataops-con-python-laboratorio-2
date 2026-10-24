"""Fixtures compartidas: un entorno completo y aislado en tmp_path.

Cada prueba recibe datos, referencia y clave propios creados con
PreparadorEntorno; la clave se inyecta en DATAOPS_KEY con monkeypatch y nunca
se imprime. Las pruebas no dependen de los archivos locales del repositorio.
"""
import contextlib
import io
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from preparar import PreparadorEntorno  # noqa: E402


@dataclass
class Entorno:
    """Rutas de un entorno de práctica temporal."""

    base: Path
    entrada: Path
    referencia: Path
    clave: Path
    salidas: Path

    def alterar_entrada(self, nombre='pedidos_prueba_parte1.csv'):
        """Crea una copia de la entrada con 1850.00 cambiado por 1851.00.

        Argumentos:
            nombre: nombre del archivo de la copia dentro de datos/.

        Devuelve:
            Ruta de la copia alterada.
        """
        copia = self.entrada.parent / nombre
        contenido = self.entrada.read_bytes()
        alterado = contenido.replace(b'1850.00', b'1851.00', 1)
        assert alterado != contenido
        copia.write_bytes(alterado)
        return copia


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    """Prepara un entorno completo en tmp_path e inyecta DATAOPS_KEY."""
    preparador = PreparadorEntorno(tmp_path)
    with contextlib.redirect_stdout(io.StringIO()):
        preparador.preparar()
    clave = preparador.clave.read_text(encoding='ascii').strip()
    monkeypatch.setenv('DATAOPS_KEY', clave)
    return Entorno(
        base=tmp_path,
        entrada=preparador.entrada,
        referencia=preparador.referencia,
        clave=preparador.clave,
        salidas=tmp_path / 'salidas',
    )


@pytest.fixture
def entorno_proceso(entorno):
    """Variables de entorno para lanzar subprocesos con la clave cargada."""
    variables = dict(os.environ)
    variables['PYTHONIOENCODING'] = 'utf-8'
    return variables
