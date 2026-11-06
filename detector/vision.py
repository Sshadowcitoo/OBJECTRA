"""Adaptación del detector de EVA: YOLO11s-seg, OpenVINO y clases COCO.

El modelo se carga una sola vez; el bloqueo protege su uso entre solicitudes.
Las áreas son porcentajes del encuadre, no medidas físicas del objeto.
"""
import base64
from threading import Lock
from time import perf_counter

import cv2
import numpy as np
from django.conf import settings

# Traducciones de clases habituales; las demás conservan el nombre del modelo.
CLASS_NAMES = {0: "Persona", 1: "Bicicleta", 2: "Automóvil", 3: "Motocicleta", 5: "Autobús", 7: "Camión", 15: "Gato", 16: "Perro", 24: "Mochila", 25: "Paraguas", 26: "Bolso", 28: "Maleta", 39: "Botella", 40: "Copa", 41: "Taza", 42: "Tenedor", 43: "Cuchillo", 44: "Cuchara", 45: "Tazón", 46: "Banano", 47: "Manzana", 48: "Sándwich", 49: "Naranja", 50: "Brócoli", 51: "Zanahoria", 52: "Hot dog", 53: "Pizza", 54: "Dona", 55: "Pastel", 56: "Silla", 57: "Sofá", 58: "Planta", 59: "Cama", 60: "Mesa de comedor", 62: "Televisor", 63: "Laptop", 64: "Mouse", 65: "Control remoto", 66: "Teclado", 67: "Celular", 73: "Libro", 74: "Reloj", 76: "Tijeras"}
_model = None
_models = {}
_lock = Lock()


def analyze(image_bytes, confidence, quality="fast"):
    global _model
    frame = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("La imagen no es válida.")
    height, width = frame.shape[:2]
    if height * width > 1920 * 1080:
        raise ValueError("La imagen debe ser como máximo de 1920 × 1080.")
    started = perf_counter()
    if quality not in settings.QUALITY_MODELS:
        raise ValueError("Selecciona una calidad válida.")
    image_size, model_path = settings.QUALITY_MODELS[quality]
    with _lock:
        model = _model if quality == "fast" else _models.get(quality)
        if model is None:
            if not model_path.exists():
                raise FileNotFoundError("Falta el modelo local. Revisa YOLO_MODEL_PATH.")
            from ultralytics import YOLO
            model = YOLO(str(model_path), task="segment")
            if quality == "fast":
                _model = model
            else:
                _models[quality] = model
        result = model.predict(frame, classes=None, conf=confidence, imgsz=image_size, retina_masks=False, verbose=False)[0]
    model_names = result.names if isinstance(result.names, dict) else dict(enumerate(result.names))
    result.names = {class_id: CLASS_NAMES.get(class_id, name) for class_id, name in model_names.items()}
    detections = []
    if result.boxes is not None:
        for i, box in enumerate(result.boxes):
            class_id = int(box.cls.item())
            area = None
            if result.masks is not None:
                mask = result.masks.data[i].cpu().numpy()
                area = round(float(np.count_nonzero(mask > 0.5)) / mask.size * 100, 2)
            x1, y1, x2, y2 = box.xyxyn[0].cpu().tolist()
            detections.append({"class_id": class_id, "name": result.names.get(class_id, str(class_id)), "confidence": round(float(box.conf.item()), 4), "area_percent": area, "box": [round(float(v), 5) for v in (x1, y1, x2, y2)]})
    annotated = result.plot()
    ok, encoded = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not ok:
        raise RuntimeError("No se pudo generar la imagen del resultado.")
    return {"detections": detections, "processing_ms": round((perf_counter() - started) * 1000), "image": "data:image/jpeg;base64," + base64.b64encode(encoded).decode("ascii")}