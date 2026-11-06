# Modelos de OBJECTRA

OBJECTRA usa exportaciones OpenVINO de YOLO11s-seg sobre COCO. Para ejecutar el código de este repositorio, coloca las exportaciones que distribuye el equipo directamente en `models/`.

| Calidad | Entrada | Carpeta |
| --- | --- | --- |
| Rápido | 320 × 320 | `yolo11s-seg-eva-320_openvino_model` |
| Equilibrado | 480 × 480 | `yolo11s-seg-eva-480_openvino_model` |
| Detalle | 640 × 640 | `yolo11s-seg_openvino_model` |

Cada carpeta debe contener `metadata.yaml` y el par de archivos `.xml` y `.bin` de la misma exportación. `YOLO_MODEL_PATH` permite cambiar la ruta de Rápido. Las demás rutas se definen en `QUALITY_MODELS` en [config/settings.py](../config/settings.py).

El paquete `OBJECTRA-Demo-Windows-EVA.zip` incluye las mismas tres exportaciones de EVA que usa la copia de referencia del equipo. Se distribuyen aparte del código en Git. Conserva los metadatos, la atribución y la documentación de licencia que acompañan a los pesos.
