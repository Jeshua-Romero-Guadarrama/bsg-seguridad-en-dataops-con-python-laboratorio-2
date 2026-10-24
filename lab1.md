# Laboratorio 1A y laboratorio 1B

Completa primero [preparar.md](preparar.md). Ambos tramos editan el mismo [lab1.py](lab1.py).

# Laboratorio 1A Protección e integridad

Duración: 25 minutos, incluida la revisión. Objetivo: comprobar que puedes recuperar un dato cifrado y detectar una modificación del CSV antes de integrar el pipeline.

## 1 Completa las funciones en lab1.py

Implementa TODO 1, 3 y 4 en ese orden. Conserva TODO 2 pendiente hasta 1B. Mantén los nombres, parámetros y contratos de las funciones.

| TODO | Función | Contrato |
| --- | --- | --- |
| 1 | calcular_hash | Recibe una ruta y devuelve SHA-256 hexadecimal sobre los bytes del archivo. |
| 3 | cifrar | Recibe texto; convierte a UTF-8, cifra con Fernet y devuelve el token como texto ASCII. |
| 4 | descifrar | Recibe token ASCII, descifra con Fernet y devuelve el texto UTF-8 original. |

Usa las APIs de hashlib y el objeto Fernet recibido. No generes otra clave dentro de estas funciones. El hash permite comparar la entrada con una referencia confiable; no cifra el contenido ni se usa aquí para contraseñas.

## 2 Guarda y ejecuta las pruebas aisladas

```text
python comprobar_1a.py
```

El comprobador importa lab1.py y utiliza tus funciones. No contiene su solución ni ejecuta el pipeline completo. Muestra estos resultados en orden:

```text
Recuperacion coincidente: True
Original coincide con referencia: True
Copia alterada coincide con referencia: False
Laboratorio 1A verificado
```

El comprobador crea datos/pedidos_prueba_parte1.csv y cambia solo 1850.00 por 1851.00 en esa copia. Se reutilizará en 1B. El original y referencia.sha256 deben permanecer intactos.

## 3 Explica la evidencia antes de continuar

¿Qué protege el cifrado? ¿Por qué debe recuperarse el mismo correo? ¿Por qué la copia devuelve False? Guarda tu explicación en evidencias.md. No ejecutes todavía lab1.py ejecutar: autorizar conserva el TODO 2. Continúa con 1B después del descanso y del bloque de acceso.

# Laboratorio 1B Autorización e integración

Duración: 35 minutos, incluida la revisión. Parte de 1A verificado, la misma entrada y la misma clave. Objetivo: permitir únicamente las operaciones asignadas y conectar los controles con el pipeline.

## 1 Completa TODO 2 en lab1.py

Implementa autorizar con PERMISOS. Si el rol tiene la operación, permite continuar. Si no la tiene o el rol es desconocido, lanza PermissionError con un mensaje sin datos personales. No concedas permisos por defecto.

| Rol | Ejecutar | Resumen | Recuperar |
| --- | --- | --- | --- |
| operador | Sí | No | Sí |
| analista | No | Sí | No |
| auditor | No | No | No |

PERMISOS también reserva evidencias para auditor. Esta entrega no implementa esa operación. El argumento --rol simula una identidad ya autenticada; no autentica al usuario ni aplica aislamiento del sistema de archivos.

## 2 Ejecuta las operaciones permitidas en orden

```text
python lab1.py ejecutar --rol operador
python lab1.py resumen --rol analista
python lab1.py recuperar --rol operador
```

El primer comando debe indicar Proceso terminado: 12 filas y crear salidas/lab1. El segundo muestra el resumen. El tercero recupera solo la primera muestra ficticia: nombre_cliente Cliente Prueba 001 y correo cliente001@example.com.

## 3 Contrasta el resultado comercial

| Ciudad | total_ventas |
| --- | --- |
| Merida | 4000.00 |
| Puebla | 2500.00 |
| Villahermosa | 4250.00 |
| Total de control | 10750.00 |

salidas/lab1/detalle_protegido.csv contiene 12 filas de datos, con nombre y correo cifrados. salidas/lab1/resumen.csv tiene tres filas de datos, además del encabezado ciudad,total_ventas. Los tres cancelados no suman. Los tokens Fernet pueden variar entre cifrados.

# Pruebas de denegación e integridad

## 4 Comprueba que los permisos bloquean

Ejecuta cada comando por separado. Usa destinos nuevos para distinguir un bloqueo de una salida anterior.

```text
python lab1.py ejecutar --rol analista --destino salidas/denegada_analista

python lab1.py ejecutar --rol desconocido --destino salidas/denegada_desconocido

python lab1.py recuperar --rol auditor
```

Esperado: BLOQUEADO por permisos. No deben crearse salidas/denegada_analista ni salidas/denegada_desconocido. El auditor no debe recuperar la muestra.

## 5 Comprueba que una entrada alterada bloquea

Reutiliza la copia datos/pedidos_prueba_parte1.csv creada en 1A. Si falta, ejecuta de nuevo comprobar_1a.py con los TODO de 1A completos.

```text
python lab1.py ejecutar --rol operador --entrada datos/pedidos_prueba_parte1.csv --destino salidas/alterada
```

Esperado: BLOQUEADO: Integridad de entrada no valida y ausencia de salidas/alterada. No actualices referencia.sha256 para hacer pasar la prueba.

## 6 Repite sin sobrescribir resultados

El pipeline rechaza un destino que ya existe. Para repetir las tres operaciones permitidas, usa el mismo destino nuevo en las tres llamadas. Sustituye lab1_repeticion por otro nombre si ya existe.

```text
python lab1.py ejecutar --rol operador --destino salidas/lab1_repeticion
python lab1.py resumen --rol analista --destino salidas/lab1_repeticion
python lab1.py recuperar --rol operador --destino salidas/lab1_repeticion
```

Los bloqueos de permisos e integridad terminan con código de salida 1; los TODO pendientes, con 2. Un bloqueo esperado es una prueba satisfactoria del control.

# Evidencias y cierre del laboratorio

## Qué debes conservar

- lab1.py con los cuatro TODO completados y comprobar_1a.py verificado.

- detalle_protegido.csv y resumen.csv de una ejecución válida, dentro de tu entorno local.

- evidencias.md con el resultado real de cada prueba y una explicación breve de los controles.

Conserva localmente la entrada, su copia alterada, la referencia y la clave para reproducir tus resultados. No adjuntes la clave a la entrega ni la muestres en capturas. Las evidencias pueden registrar estados y rutas sin copiar datos recuperados o tokens.

## Cómo reconocer una práctica completa

Debes observar True, True y False en 1A; 12 filas procesadas y los totales correctos en 1B; denegación para analista, desconocido y recuperación del auditor; y bloqueo de la copia alterada sin crear su destino. Documenta lo observado, incluso si una prueba falla.

## Si algo falla

| Síntoma | Qué revisar |
| --- | --- |
| ModuleNotFoundError | Instala requirements.txt con el intérprete del entorno virtual. |
| PENDIENTE | Completa el TODO indicado. En 1A, autorizar sigue pendiente por diseño. |
| Falta DATAOPS_KEY | Carga la clave en la misma terminal que ejecuta Python. |
| InvalidToken o clave inválida | Comprueba que usas la clave original y un token sin modificar. No regeneres claves para recuperar salidas. |
| El destino ya existe | Usa un destino nuevo para la ejecución y el mismo para sus consultas. |
| El original no coincide | Detén el procesamiento y revisa su origen. No recalcules la referencia para ocultar el fallo. |

## Aprender el control y reconocer sus límites

El laboratorio no es una arquitectura de producción. El original permanece legible; el cifrado no anonimiza los identificadores restantes. Los roles se simulan en la aplicación y un usuario con acceso local puede leer archivos directamente. La referencia y la clave requieren protección propia.

Explica qué añadirías en producción: identidad verificable, permisos del sistema, gestión de secretos, respaldos y trazabilidad. La pregunta de cierre es qué riesgo detectaste, qué control aplicaste y con qué prueba demostraste su comportamiento.

## Código base completo de lab1.py

Este listado conserva los cuatro TODO y coincide con el archivo inicial. Guarda tus cambios en lab1.py.

```python
import argparse
import csv
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path
from cryptography.fernet import Fernet

BASE = Path(__file__).resolve().parent
DATOS = BASE / 'datos'
SALIDAS = BASE / 'salidas'
PERMISOS = {
    'operador': {'ejecutar', 'recuperar'},
    'analista': {'resumen'},
    'auditor': {'evidencias'},
}
CAMPOS = [
    'pedido_id', 'cliente_id', 'nombre_cliente',
    'correo', 'ciudad', 'importe', 'estado',
]


def calcular_hash(ruta):
    # TODO 1: devolver el SHA-256 hexadecimal del archivo.
    raise NotImplementedError('TODO 1: calcular_hash')


def autorizar(rol, operacion):
    # TODO 2: usar PERMISOS; denegar roles desconocidos.
    # Sin permiso: lanzar PermissionError, sin datos personales.
    raise NotImplementedError('TODO 2: autorizar')


def cifrar(valor, fernet):
    # TODO 3: str -> UTF-8 -> encrypt -> texto ASCII.
    raise NotImplementedError('TODO 3: cifrar')


def descifrar(token, fernet):
    # TODO 4: texto ASCII -> decrypt -> texto UTF-8.
    raise NotImplementedError('TODO 4: descifrar')


def cargar_cifrador():
    clave = os.environ.get('DATAOPS_KEY')
    if not clave:
        raise ValueError('Falta DATAOPS_KEY en el entorno')
    return Fernet(clave.encode('ascii'))


def leer_pedidos(ruta):
    with Path(ruta).open(encoding='utf-8', newline='') as f:
        lector = csv.DictReader(f)
        if lector.fieldnames != CAMPOS:
            raise ValueError('Columnas distintas del contrato')
        filas = list(lector)
    if not filas:
        raise ValueError('Dataset vacio')
    ids = [fila['pedido_id'] for fila in filas]
    if len(ids) != len(set(ids)):
        raise ValueError('Identificadores duplicados')
    for fila in filas:
        monto = Decimal(fila['importe'])
        if not monto.is_finite() or monto < 0:
            raise ValueError('Importe invalido')
        if fila['estado'] not in {'Confirmado', 'Cancelado'}:
            raise ValueError('Estado invalido')
    return filas


def verificar_integridad(entrada, referencia):
    esperado = Path(referencia).read_text().strip()
    actual = calcular_hash(entrada)
    if actual != esperado:
        raise ValueError('Integridad de entrada no valida')
    return actual


def escribir_csv(ruta, campos, filas):
    with Path(ruta).open('w', encoding='utf-8', newline='') as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def ejecutar(rol, entrada, referencia, destino):
    autorizar(rol, 'ejecutar')
    hash_entrada = verificar_integridad(entrada, referencia)
    filas = leer_pedidos(entrada)
    fernet = cargar_cifrador()
    protegidas, totales = [], {}
    for fila in filas:
        copia = dict(fila)
        for campo in ('nombre_cliente', 'correo'):
            copia[campo] = cifrar(fila[campo], fernet)
        protegidas.append(copia)
        if fila['estado'] == 'Confirmado':
            ciudad = fila['ciudad']
            totales[ciudad] = (
                totales.get(ciudad, Decimal('0'))
                + Decimal(fila['importe'])
            )
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=False)
    detalle = destino / 'detalle_protegido.csv'
    resumen = destino / 'resumen.csv'
    escribir_csv(detalle, CAMPOS, protegidas)
    escribir_csv(resumen, ['ciudad', 'total_ventas'], [
        {'ciudad': ciudad, 'total_ventas': f'{total:.2f}'}
        for ciudad, total in sorted(totales.items())
    ])
    return {
        'hash_entrada': hash_entrada,
        'filas': len(filas),
        'detalle': detalle,
        'resumen': resumen,
    }


def consultar_resumen(rol, destino):
    autorizar(rol, 'resumen')
    ruta = Path(destino) / 'resumen.csv'
    return ruta.read_text(encoding='utf-8')


def recuperar_muestra(rol, destino):
    autorizar(rol, 'recuperar')
    ruta = Path(destino) / 'detalle_protegido.csv'
    fila = leer_pedidos(ruta)[0]
    fernet = cargar_cifrador()
    return {
        campo: descifrar(fila[campo], fernet)
        for campo in ('nombre_cliente', 'correo')
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('accion', choices=[
        'inspeccionar', 'ejecutar', 'resumen', 'recuperar',
    ])
    parser.add_argument('--rol', default='operador')
    parser.add_argument('--entrada', type=Path,
                        default=DATOS / 'pedidos.csv')
    parser.add_argument('--referencia', type=Path,
                        default=BASE / 'referencia.sha256')
    parser.add_argument('--destino', type=Path,
                        default=SALIDAS / 'lab1')
    args = parser.parse_args()
    try:
        if args.accion == 'inspeccionar':
            # Diagnostico previo con datos ficticios.
            print(json.dumps(leer_pedidos(args.entrada)[0],
                             ensure_ascii=False, indent=2))
        elif args.accion == 'ejecutar':
            r = ejecutar(args.rol, args.entrada,
                         args.referencia, args.destino)
            print(f"Proceso terminado: {r['filas']} filas")
        elif args.accion == 'resumen':
            print(consultar_resumen(args.rol, args.destino))
        else:
            print(json.dumps(recuperar_muestra(
                args.rol, args.destino), ensure_ascii=False))
    except NotImplementedError as exc:
        parser.exit(2, f'PENDIENTE: {exc}\n')
    except (PermissionError, ValueError, OSError) as exc:
        parser.exit(1, f'BLOQUEADO: {exc}\n')


if __name__ == '__main__':
    main()
```

## Referencias técnicas

- [Fernet](https://cryptography.io/en/stable/fernet/)
- [hashlib de Python 3.12](https://docs.python.org/3.12/library/hashlib.html)
- [cryptography 50.0.2](https://pypi.org/project/cryptography/50.0.2/)
