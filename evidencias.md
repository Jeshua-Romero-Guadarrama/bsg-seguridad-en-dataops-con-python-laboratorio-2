# Evidencias del laboratorio 1

Participante: Jeshua Romero Guadarrama  Fecha: 23-10-2026

Registra lo que observaste realmente. No pegues claves, tokens ni datos recuperados.

Entorno: Windows 11, Python 3.12.10, cryptography 50.0.2, entorno virtual `.venv`. La clave se cargó en la terminal con `DATAOPS_KEY` desde `.secrets/fernet.key` sin mostrarla. Las muestras recuperadas son los valores ficticios que el propio material publica en `lab1.md`; no se copian tokens.

| Prueba | Resultado esperado | Resultado observado | Explicación o corrección |
| --- | --- | --- | --- |
| Recuperar correo en 1A | True | `python comprobar_1a.py`: `Recuperacion coincidente: True` (código 0) | Fernet cifra el correo y la misma clave devuelve exactamente el texto original. |
| Comparar original | True | `Original coincide con referencia: True` | El SHA-256 de `datos/pedidos.csv` coincide con `referencia.sha256`; ninguno de los dos se modificó. |
| Comparar copia alterada | False | `Copia alterada coincide con referencia: False` y `Laboratorio 1A verificado` | `datos/pedidos_prueba_parte1.csv` solo cambia 1850.00 por 1851.00 y la huella ya no coincide. |
| Ejecutar como operador | 12 filas | `python lab1.py ejecutar --rol operador`: `Proceso terminado: 12 filas` (código 0); se creó `salidas/lab1` | Superó permiso, integridad y contrato antes de cifrar y escribir. |
| Consultar como analista | 3 ciudades y total 10750.00 | `python lab1.py resumen --rol analista`: `Merida,4000.00`, `Puebla,2500.00`, `Villahermosa,4250.00` (código 0); suma 10750.00 | Los tres pedidos cancelados (1200.00, 800.00 y 550.00) no suman. |
| Recuperar como operador | Muestra ficticia coincidente | `python lab1.py recuperar --rol operador`: JSON con nombre_cliente y correo de la primera fila, coincidentes con la muestra ficticia indicada en `lab1.md` (código 0) | Solo se descifra la primera fila y solo con el rol autorizado. |
| Ejecutar como analista | Bloqueado sin destino nuevo | `BLOQUEADO: Rol 'analista' sin permiso para 'ejecutar'` (código 1); `ls salidas/denegada_analista`: No such file or directory | El permiso se comprueba antes de leer o escribir nada. |
| Ejecutar con rol desconocido | Bloqueado sin destino nuevo | `BLOQUEADO: Rol desconocido: 'desconocido'` (código 1); `ls salidas/denegada_desconocido`: No such file or directory | No hay permisos por defecto: un rol fuera de la matriz se deniega. |
| Recuperar como auditor | Bloqueado | `BLOQUEADO: Rol 'auditor' sin permiso para 'recuperar'` (código 1); no se mostró ningún dato | El auditor solo tiene reservada `evidencias`, que esta entrega no implementa. |
| Procesar copia alterada | Bloqueado sin salidas/alterada | `python lab1.py ejecutar --rol operador --entrada datos/pedidos_prueba_parte1.csv --destino salidas/alterada`: `BLOQUEADO: Integridad de entrada no valida` (código 1); `ls salidas/alterada`: No such file or directory | La referencia no se recalculó; tras la prueba, `datos/pedidos.csv` sigue coincidiendo con `referencia.sha256`. |

### Pruebas complementarias observadas

| Prueba | Resultado observado |
| --- | --- |
| Repetición en `salidas/lab1_repeticion` | `ejecutar --rol operador`: `Proceso terminado: 12 filas`; `resumen --rol analista`: las mismas tres ciudades; `recuperar --rol operador`: la misma muestra ficticia. Las tres con código 0. |
| Repetir sobre `salidas/lab1` existente | `BLOQUEADO: [WinError 183] No se puede crear un archivo que ya existe: '...\salidas\lab1'` (código 1); los archivos previos no se sobrescribieron. |
| Ejecutar sin `DATAOPS_KEY` (destino `salidas/sin_clave`) | `BLOQUEADO: Falta DATAOPS_KEY en el entorno` (código 1); el destino no se creó. |
| Contenido final de `salidas/` | Solo `lab1` y `lab1_repeticion`. No existen `denegada_analista`, `denegada_desconocido`, `alterada` ni `sin_clave`. |
| Pruebas automatizadas | `python -m pytest -q`: 54 pruebas superadas. |

## Archivos de salida

Destino válido utilizado: `salidas/lab1` (repetición independiente en `salidas/lab1_repeticion`)

Filas de detalle: 12  Filas de resumen: 3

Totales observados por ciudad: Merida 4000.00, Puebla 2500.00, Villahermosa 4250.00; total de control 10750.00

En `salidas/lab1/detalle_protegido.csv`, las columnas `nombre_cliente` y `correo` contienen tokens Fernet (ninguna celda contiene `@` ni `Cliente Prueba`); `pedido_id`, `cliente_id`, `ciudad`, `importe` y `estado` quedan iguales al original.

## Reflexión

1. **¿Qué protege cada control y qué prueba lo demuestra?** El cifrado Fernet protege la confidencialidad del nombre y el correo en las salidas: la prueba de 1A recupera el mismo correo (True) y el detalle de `salidas/lab1` solo muestra tokens, mientras que `recuperar --rol operador` demuestra que el dato sigue siendo recuperable con la clave correcta. La huella SHA-256 frente a la referencia protege la integridad de la entrada: el original da True, la copia con 1851.00 da False y el pipeline la bloquea con `Integridad de entrada no valida` sin crear `salidas/alterada`. La autorización por rol protege qué operación puede hacer cada perfil: el analista y el rol desconocido no pueden ejecutar y el auditor no puede recuperar, y en ningún caso aparece el destino. La validación del contrato protege la calidad del cálculo (columnas, identificadores, importes y estados), y la regla de no sobrescribir protege las salidas ya aceptadas, como se vio al repetir sobre `salidas/lab1`.

2. **¿Por qué no debes recalcular la referencia ante una alteración?** La referencia es el alta confiable del original conocido; su valor está precisamente en que no cambia cuando cambian los datos. Si la recalculo para que la copia alterada pase, convierto el control en un sello que acepta cualquier contenido y borro la evidencia de que algo cambió. Ante una discrepancia lo correcto es detener el procesamiento, investigar el origen del archivo y, si el cambio es legítimo, registrar una nueva referencia mediante un proceso controlado y trazable, no desde la misma terminal que procesa los datos.

3. **¿Por qué --rol no equivale a autenticar una identidad?** El argumento `--rol` es un texto que escribe quien lanza el comando: nadie verifica que esa persona sea realmente operador. Cualquiera con acceso a la terminal puede escribir `--rol operador` y obtener los permisos. Además, el control vive dentro de la aplicación: un usuario con acceso local puede leer `datos/pedidos.csv` o `.secrets/fernet.key` directamente sin pasar por `lab1.py`. La matriz demuestra la lógica de autorización, pero la autenticación necesita una identidad verificable y permisos aplicados por el sistema.

4. **¿Qué riesgos quedan en el original, los identificadores y la clave?** El original `datos/pedidos.csv` permanece legible en disco y no se borra ni se cifra. Los identificadores `pedido_id` y `cliente_id`, junto con ciudad e importe, siguen en claro: el cifrado no anonimiza y permite relacionar pedidos de un mismo cliente (CLI-001 aparece dos veces). La clave está en un archivo local junto a los datos; en Windows el `chmod 0o600` no restringe el acceso, y quien obtenga la clave y el detalle puede descifrarlo todo. Si la clave se pierde, las salidas cifradas son irrecuperables, como confirma la prueba que obtiene InvalidToken con otra clave. Por último, la referencia también es local y quien pueda modificar entrada y referencia a la vez burlaría el control.

5. **¿Qué añadirías para utilizar este enfoque en producción?** Una identidad verificable (inicio de sesión corporativo con MFA o identidades de servicio) en lugar de `--rol`, y permisos del sistema de archivos o del almacenamiento que impidan leer el original y la clave a quien no corresponda. Guardaría la clave en un gestor de secretos con rotación periódica y procedimiento de recifrado, nunca en un archivo junto a los datos. Añadiría respaldos de las salidas y de la clave con restauraciones probadas, trazabilidad de cada ejecución y denegación (quién, cuándo, qué operación, qué huella de entrada) en un registro de auditoría inalterable, e implementaría la operación `evidencias` del auditor sobre ese registro. Finalmente, publicaría la referencia en un almacén con versiones protegidas y aprobación separada, de modo que nadie pueda cambiar a la vez los datos y su huella confiable.
