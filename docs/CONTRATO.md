# Contrato de la aplicación

## Pantallas y endpoints

| Método | Ruta | Función |
| --- | --- | --- |
| GET | `/` | Detector con cámara, carga de imagen, ejemplo y comparador |
| GET | `/historial/` | Capturas guardadas, hasta 12 por página |
| POST | `/api/detect/` | Analizar una imagen o un fotograma |
| POST | `/api/save/` | Guardar el resultado firmado por el servidor |

Los POST usan la protección CSRF de Django. El cliente envía el encabezado `X-CSRFToken`.

## Analizar

`POST /api/detect/` recibe `multipart/form-data`.

| Campo | Valor |
| --- | --- |
| `frame` | Archivo de imagen no vacío de hasta 2 MB y hasta 2.073.600 píxeles |
| `confidence` | Umbral entre 0.10 y 0.90. Predeterminado: 0.25 |
| `quality` | `fast`, `balanced` o `detail`. Predeterminado: `fast` |
| `source` | El cliente usa `camera`, `upload` o `example` |

El resultado JSON incluye `detections`, `processing_ms`, `image` (JPEG como data URL), `token` y `can_save`. Cada detección contiene `class_id`, `name`, `confidence`, `area_percent` y `box` con las coordenadas normalizadas `[x1, y1, x2, y2]`. `area_percent` describe el área de la máscara dentro de la imagen cuando hay máscara disponible. La API responde con 400 para entradas inválidas y 503 cuando el análisis no está disponible.

El servidor omite el token si la fuente es `example` o si el contenido coincide con el archivo de ejemplo por SHA-256, aunque se haya renombrado.

## Guardar

`POST /api/save/` recibe `token` como campo de formulario. El servidor verifica la firma y una vigencia máxima de 900 segundos, crea la captura y responde con HTTP 201 y su `id`. La interfaz bloquea ambos controles de guardado mientras una solicitud está pendiente.
