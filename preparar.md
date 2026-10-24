# Preparación del laboratorio 1

Realiza esta preparación antes de la sesión. Necesitas Python 3.12 con venv y pip, un editor de código y una terminal. La conexión a Internet se utiliza para instalar dependencias. Entorno comprobado: Python 3.12.14 y cryptography 50.0.2 en Linux; los comandos de PowerShell se proporcionan como alternativa.

## 1 Abre la carpeta de trabajo

Trabaja dentro de comercial_nova, donde están preparar.py, lab1.py y requirements.txt. No ejecutes comandos desde el interior del ZIP. Si el comando python no existe, localiza tu instalación de Python antes de continuar.

## 2 Crea e instala en Windows PowerShell

```text
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, no cambies las políticas del equipo. Instala con el intérprete del entorno y sustituye python por .\.venv\Scripts\python.exe en los comandos posteriores.

```text
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Alternativa en WSL o Linux

```text
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Elige una sola alternativa. No mezcles un entorno virtual de Windows con WSL. Si falta venv o pip, solicita apoyo para completar la instalación de Python.

## 3 Comprueba la dependencia

```text
python --version
python -c "import cryptography; print(cryptography.__version__)"
```

La dependencia debe mostrar 50.0.2. hashlib, csv, argparse, json, os, decimal y pathlib pertenecen a la biblioteca estándar y no se instalan por separado. requirements.txt fija la dependencia directa; pip resuelve sus dependencias transitivas.

## 4 Genera el entorno una sola vez

```text
python preparar.py
```

Resultado esperado: Dataset, referencia y clave creados sin mostrarlos. El programa crea estos archivos y no los reemplaza si ya existen.

| Ruta | Uso |
| --- | --- |
| datos/pedidos.csv | Dataset original de 12 pedidos ficticios |
| referencia.sha256 | Huella del original conocido para comparar |
| .secrets/fernet.key | Clave local generada para tu práctica |

No edites el original ni recalcules la referencia para aceptar un archivo sospechoso. La referencia local representa un alta inicial confiable; no tiene protección independiente frente a quien puede modificar ambos archivos.

## 5 Carga la clave en la terminal actual

En Windows PowerShell:

```text
$env:DATAOPS_KEY = (Get-Content .secrets/fernet.key -Raw).Trim()
```

En WSL o Linux:

```text
export DATAOPS_KEY="$(cat .secrets/fernet.key)"
```

Vuelve a cargarla al abrir otra terminal. No imprimas la clave ni la copies al código, Git, capturas o evidencias. Una clave nueva no recupera salidas cifradas con otra clave. .gitignore excluye datos, secretos y salidas; no elimina archivos ya versionados.

## 6 Inspecciona el punto de partida

```text
python lab1.py inspeccionar
```

Verás el primer pedido ficticio, incluido cliente001@example.com. Esta inspección previa omite permisos de forma intencional; sirve para identificar qué campos proteger. No representa una operación segura de producción.

Contrato de columnas, en orden: pedido_id, cliente_id, nombre_cliente, correo, ciudad, importe, estado. No cambies los nombres. Si ya existe el entorno, consérvalo; para una práctica nueva utiliza otra copia de la carpeta.

## Código completo de preparar.py

Este listado coincide con el archivo ejecutable. El dataset completo está definido en PEDIDOS. No ejecutes este Markdown con Python.

```python
import csv
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet

BASE = Path(__file__).resolve().parent
CAMPOS = [
    'pedido_id', 'cliente_id', 'nombre_cliente',
    'correo', 'ciudad', 'importe', 'estado',
]
# Todos los clientes y pedidos son ficticios.
# Numero de cliente, ciudad, importe y estado por pedido.
PEDIDOS = [
    (1, 'Villahermosa', '1850.00', 'Confirmado'),
    (2, 'Merida', '950.50', 'Confirmado'),
    (3, 'Puebla', '1200.00', 'Cancelado'),
    (1, 'Villahermosa', '650.00', 'Confirmado'),
    (4, 'Merida', '1499.50', 'Confirmado'),
    (5, 'Puebla', '2100.00', 'Confirmado'),
    (6, 'Villahermosa', '800.00', 'Cancelado'),
    (7, 'Puebla', '400.00', 'Confirmado'),
    (8, 'Merida', '300.00', 'Confirmado'),
    (9, 'Villahermosa', '1750.00', 'Confirmado'),
    (10, 'Puebla', '550.00', 'Cancelado'),
    (11, 'Merida', '1250.00', 'Confirmado'),
]


def main():
    datos = BASE / 'datos'
    secretos = BASE / '.secrets'
    datos.mkdir(exist_ok=True)
    secretos.mkdir(exist_ok=True)
    entrada = datos / 'pedidos.csv'
    referencia = BASE / 'referencia.sha256'
    clave = secretos / 'fernet.key'
    # No reemplazar datos, clave o referencia en una repeticion.
    if any(p.exists() for p in (entrada, referencia, clave)):
        raise FileExistsError('Entorno existente; revisar antes de recrear')
    with entrada.open('w', encoding='utf-8', newline='') as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        escritor.writeheader()
        for n, (cliente, ciudad, importe, estado) in enumerate(
                PEDIDOS, start=1001):
            escritor.writerow({
                'pedido_id': f'PED-{n}',
                'cliente_id': f'CLI-{cliente:03d}',
                'nombre_cliente': f'Cliente Prueba {cliente:03d}',
                'correo': f'cliente{cliente:03d}@example.com',
                'ciudad': ciudad,
                'importe': importe,
                'estado': estado,
            })
    # Alta de referencia sobre datos conocidos del instructor.
    referencia.write_text(
        hashlib.sha256(entrada.read_bytes()).hexdigest(),
        encoding='ascii')
    with clave.open('xb') as f:
        f.write(Fernet.generate_key())
    try:
        clave.chmod(0o600)
    except OSError:
        pass  # En Windows se requiere gestionar ACL aparte.
    print('Dataset, referencia y clave creados sin mostrarlos')


if __name__ == '__main__':
    main()
```
