# Modelos previstos para OBJECTRA

La integración del detector corresponde a la siguiente etapa de JHOAN. Los modelos reutilizados de EVA se distribuyen aparte del repositorio; no se suben pesos ni entornos virtuales.

Exportaciones de referencia:
- Rápido 320: `yolo11s-seg-eva-320_openvino_model`.
- Equilibrado 480: `yolo11s-seg-eva-480_openvino_model`.
- Detalle 640: `yolo11s-seg_openvino_model`.

Cada carpeta conserva sus archivos `.xml`, `.bin` y `metadata.yaml`. Son pesos YOLO11s-seg sobre COCO exportados a OpenVINO. Conservar atribución y revisar las condiciones de su licencia AGPL-3.0 antes de distribuirlos.
