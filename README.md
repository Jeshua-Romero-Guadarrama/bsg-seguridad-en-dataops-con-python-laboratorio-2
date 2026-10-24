# Comercial Nova · Laboratorio 2: pipeline completo con control de acceso, integridad y validación

Solución del **tramo 1B (Autorización e integración)** del curso de DataOps Security sobre el caso ficticio Comercial Nova. El repositorio parte de los controles del tramo 1A (huella SHA-256 y cifrado Fernet) y completa el pipeline: matriz de roles, caso autorizado de extremo a extremo y pruebas de bloqueo que demuestran que una operación denegada o una entrada alterada nunca producen salidas.

## Objetivo del laboratorio

Permitir únicamente las operaciones asignadas a cada rol y conectar los controles en un orden fijo dentro del pipeline:

1. **Permiso**: el rol debe tener la operación en la matriz.
2. **Integridad**: la huella de la entrada debe coincidir con la referencia confiable.
3. **Validación**: el CSV cumple el contrato de columnas, identificadores, importes y estados.
4. **Cifrado**: `nombre_cliente` y `correo` se convierten en tokens Fernet.
5. **Escritura**: el destino se crea solo al final y nunca se sobrescribe.

Los cuatro TODO de `lab1.py` están implementados. Duración prevista del tramo: 35 minutos.

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `lab1.py` | Pipeline orientado a objetos con los cuatro TODO resueltos y la CLI. |
| `preparar.py` | `PreparadorEntorno`: genera dataset, referencia y clave sin mostrarlos. |
| `comprobar_1a.py` | Comprobador del tramo 1A; admite `--base <carpeta>`. |
| `pruebas/` | Pruebas pytest con entornos aislados en `tmp_path`. |
| `pytest.ini` | Convenciones de nombres de pytest en español. |
| `evidencias.md` | Resultados reales observados y reflexión. |
| `salidas/lab1/` | Salida válida versionada: solo tokens y totales. |
| `lab1.md`, `preparar.md` | Guías originales del curso, copiadas sin cambios. |
| `.github/workflows/pruebas.yml` | Integración continua en Ubuntu y Windows. |
| `requirements.txt` | `cryptography==50.0.2` y `pytest==9.1.1`. |

Las guías `lab1.md` y `preparar.md` conservan el listado del código base original con los TODO pendientes; la solución está en los archivos `.py`.

No se versionan `datos/`, `.secrets/`, `referencia.sha256`, `.venv/` ni el resto de `salidas/`.

## Requisitos

- Python 3.12 con `venv` y `pip`.
- Conexión a Internet para instalar dependencias.

## Instalación

En Windows PowerShell:

```text
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, no cambies las políticas del equipo. Instala con el intérprete del entorno y sustituye python por `.\.venv\Scripts\python.exe` en los comandos posteriores.

```text
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En WSL o Linux:

```text
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Elige una sola alternativa; no mezcles un entorno virtual de Windows con WSL.

## Preparar el entorno y cargar la clave

```text
python preparar.py
```

Resultado esperado: `Dataset, referencia y clave creados sin mostrarlos`. Si el entorno ya existe, el programa responde `Entorno existente; revisar antes de recrear` y no reemplaza nada.

Carga la clave en la misma terminal que ejecutará Python. En PowerShell:

```text
$env:DATAOPS_KEY = (Get-Content .secrets/fernet.key -Raw).Trim()
```

En WSL o Linux:

```text
export DATAOPS_KEY="$(cat .secrets/fernet.key)"
```

No imprimas la clave ni la copies al código, a Git, a capturas o a evidencias.

## Orden exacto de comandos para reproducir

```text
python comprobar_1a.py
python lab1.py ejecutar --rol operador
python lab1.py resumen --rol analista
python lab1.py recuperar --rol operador
python lab1.py ejecutar --rol analista --destino salidas/denegada_analista
python lab1.py ejecutar --rol desconocido --destino salidas/denegada_desconocido
python lab1.py recuperar --rol auditor
python lab1.py ejecutar --rol operador --entrada datos/pedidos_prueba_parte1.csv --destino salidas/alterada
python lab1.py ejecutar --rol operador --destino salidas/lab1_repeticion
python lab1.py resumen --rol analista --destino salidas/lab1_repeticion
python lab1.py recuperar --rol operador --destino salidas/lab1_repeticion
```

Como este repositorio ya incluye `salidas/lab1`, en un clon nuevo el segundo comando responderá que el destino existe. Usa otro destino (por ejemplo `--destino salidas/mi_ejecucion`) en las tres operaciones permitidas, o elimina tu copia local de `salidas/lab1` antes de empezar. Las salidas versionadas se cifraron con la clave del autor y no pueden descifrarse con una clave nueva.

## Matriz de roles

| Operación | Operador | Analista | Auditor |
| --- | --- | --- | --- |
| Ejecutar | Sí | No | No |
| Resumen | No | Sí | No |
| Recuperar | Sí | No | No |
| Evidencias | No | No | Reservada (no implementada) |

Un rol desconocido o una operación no listada se deniegan con `PermissionError`; el mensaje indica rol y operación, nunca datos personales. No hay permisos por defecto. El argumento `--rol` simula una identidad ya autenticada.

## Resultados esperados

| Comprobación | Resultado esperado |
| --- | --- |
| Pedidos cifrados | `Proceso terminado: 12 filas`; 12 filas en `detalle_protegido.csv` con nombre y correo cifrados |
| Ciudades del resumen | 3 filas: Merida 4000.00, Puebla 2500.00, Villahermosa 4250.00 |
| Total de control | 10750.00 (los tres cancelados no suman) |
| Bloqueo antes de escribir | `BLOQUEADO` con código 1 y sin crear `salidas/denegada_analista`, `salidas/denegada_desconocido` ni `salidas/alterada` |

| Ciudad | total_ventas |
| --- | --- |
| Merida | 4000.00 |
| Puebla | 2500.00 |
| Villahermosa | 4250.00 |
| Total de control | 10750.00 |

Los bloqueos de permisos, integridad y validación terminan con código 1; un TODO pendiente, con código 2. Los tokens Fernet varían entre cifrados.

## Pruebas automatizadas

```text
python -m pytest -q
```

Resultado actual: 54 pruebas superadas. Cada prueba crea su propio entorno en `tmp_path` con `PreparadorEntorno` e inyecta `DATAOPS_KEY` con `monkeypatch`, de modo que no dependen de `datos/`, `.secrets/` ni `referencia.sha256` del repositorio.

| Módulo | Qué cubre |
| --- | --- |
| `prueba_control_acceso.py` | Las 12 combinaciones rol x operación, rol y operación desconocidos, mensajes sin datos personales. |
| `prueba_pipeline.py` | Caso autorizado, detalle cifrado, resumen, consultas por rol, InvalidToken con otra clave, bloqueos sin escritura, orden de controles y repetición. |
| `prueba_interfaz.py` | CLI por subprocess (códigos 0 y 1, `BLOQUEADO`, destinos ausentes, falta de clave) y `comprobar_1a.py --base`. |
| `prueba_preparar.py` | `PreparadorEntorno` (tres archivos, 12 filas, contrato, no reemplaza), huella y cifrado. |

## Diseño de clases

| Clase | Responsabilidad |
| --- | --- |
| `CalculadoraHuella` | SHA-256 hexadecimal leyendo por bloques de 65536 bytes. |
| `CifradorCampos` | Cifrar y descifrar texto con Fernet; carga la clave desde `DATAOPS_KEY`. |
| `ControlAcceso` | Matriz de permisos; deniega roles y operaciones no listados. |
| `ValidadorPedidos` | Contrato de columnas, dataset no vacío, identificadores únicos, importes y estados. |
| `VerificadorIntegridad` | Comparar la huella de la entrada con la referencia confiable. |
| `EscritorCsv` | Escribir CSV UTF-8 con encabezado. |
| `PipelineNova` | Orquestar permiso, integridad, validación, cifrado y escritura; resumen y recuperación. |
| `InterfazLinea` | CLI con `argparse` y traducción de excepciones a códigos de salida. |
| `PreparadorEntorno` | Generar dataset, referencia y clave sin reemplazar un entorno existente. |
| `ComprobadorLaboratorio1A` | Comprobaciones del tramo 1A sobre la carpeta base elegida. |

Las funciones del material (`calcular_hash`, `autorizar`, `cifrar`, `descifrar`, `cargar_cifrador`, `leer_pedidos`, `verificar_integridad`, `escribir_csv`, `ejecutar`, `consultar_resumen`, `recuperar_muestra`, `main`) conservan nombres y contratos y delegan en estas clases.

## Riesgos, controles y pruebas

| Riesgo | Control | Prueba que lo demuestra |
| --- | --- | --- |
| Exposición de nombre y correo en las salidas | Cifrado Fernet de `nombre_cliente` y `correo` | `prueba_detalle_cifrado`: tokens `gAAAA...` sin `@` ni `Cliente Prueba` |
| Un rol ejecuta o lee lo que no le corresponde | `ControlAcceso` con denegación por defecto | `prueba_matriz_completa` (12 casos) y bloqueos por CLI |
| Procesar una entrada modificada | `VerificadorIntegridad` con referencia confiable | `prueba_entrada_alterada`: `Integridad de entrada no valida` sin destino |
| Datos que rompen el cálculo | `ValidadorPedidos` | `prueba_integridad_antes_que_contrato` y validación de la copia alterada |
| Salidas parciales tras un bloqueo | Destino creado solo al final | Pruebas de bloqueo que comprueban `not destino.exists()` |
| Pérdida de resultados aceptados | `mkdir(exist_ok=False)` | `prueba_destino_existente_no_se_sobrescribe` (comparación de bytes) |
| Clave ausente o equivocada | `CifradorCampos.desde_entorno` y Fernet | `prueba_sin_clave` y `prueba_recuperar_con_otra_clave` (InvalidToken) |

## Si algo falla

| Señal | Primera revisión |
| --- | --- |
| ModuleNotFoundError | Instala requirements.txt con el intérprete del entorno virtual. |
| PENDIENTE | Completa el TODO indicado. En 1A, autorizar sigue pendiente por diseño. |
| Falta DATAOPS_KEY | Carga la clave en la misma terminal que ejecuta Python. |
| InvalidToken o clave inválida | Comprueba que usas la clave original y un token sin modificar. No regeneres claves para recuperar salidas. |
| El destino ya existe | Usa un destino nuevo para la ejecución y el mismo para sus consultas. |
| El original no coincide | Detén el procesamiento y revisa su origen. No recalcules la referencia para ocultar el fallo. |

## Límites del laboratorio frente a producción

El laboratorio no es una arquitectura de producción. El original permanece legible y el cifrado no anonimiza los identificadores restantes. Los roles se simulan en la aplicación y un usuario con acceso local puede leer archivos directamente. La referencia y la clave requieren protección propia. En producción haría falta:

- Custodia y rotación de claves en un gestor de secretos.
- Publicación de la referencia con versiones protegidas y aprobación separada.
- Identidad verificada y permisos aplicados por el sistema, no por un argumento.
- Auditoría de cada ejecución y denegación, y recuperación probada a partir de respaldos.

## Relación con el Laboratorio 1

Este repositorio continúa el [Laboratorio 1 (tramo 1A: protección e integridad)](https://github.com/Jeshua-Romero-Guadarrama/bsg-seguridad-en-dataops-con-python-laboratorio-1), donde se implementan la huella SHA-256 y el cifrado Fernet y se verifica `comprobar_1a.py`. Aquí se reutiliza el mismo diseño de clases, se completa la autorización y se integra el pipeline completo.
