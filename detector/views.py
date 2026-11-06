import logging
import math
from functools import lru_cache
from hashlib import sha256

from django.conf import settings
from django.core import signing
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .models import Capture
from .vision import analyze

logger = logging.getLogger(__name__)
RESULT_SALT = "detector.capture.v2"


@lru_cache(maxsize=1)
def example_digest():
    path = settings.BASE_DIR / "static" / "detector" / "examples" / "street.jpg"
    return sha256(path.read_bytes()).digest() if path.is_file() else None


@require_GET
def index(request):
    return render(request, "detector/index.html", {"system_name": settings.SYSTEM_NAME})


@require_GET
def history(request):
    page = Paginator(Capture.objects.all(), 12).get_page(request.GET.get("page"))
    return render(request, "detector/history.html", {"page": page, "system_name": settings.SYSTEM_NAME})


@require_POST
def detect(request):
    upload = request.FILES.get("frame")
    if upload is None or upload.size > 2 * 1024 * 1024:
        return JsonResponse({"error": "Envía una imagen de hasta 2 MB."}, status=400)
    try:
        confidence = float(request.POST.get("confidence", "0.25"))
        if not math.isfinite(confidence) or not 0.1 <= confidence <= 0.9:
            raise ValueError("La confianza debe estar entre 0.10 y 0.90.")
        quality = request.POST.get("quality", "fast")
        if quality not in settings.QUALITY_MODELS:
            raise ValueError("Selecciona una calidad válida.")
        image_bytes = upload.read()
        is_example = request.POST.get("source") == "example" or sha256(image_bytes).digest() == example_digest()
        result = analyze(image_bytes, confidence, quality)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except FileNotFoundError as exc:
        return JsonResponse({"error": str(exc)}, status=503)
    except Exception:
        logger.exception("Error de inferencia")
        return JsonResponse({"error": "No se pudo ejecutar el detector. Revisa el modelo y el entorno local."}, status=503)
    # El guardado solo acepta resultados generados por el servidor, sin confiar
    # en etiquetas o porcentajes enviados libremente por el navegador.
    result["token"] = None if is_example else signing.dumps(result, salt=RESULT_SALT, compress=True)
    result["can_save"] = not is_example
    return JsonResponse(result)


@require_POST
def save(request):
    token = request.POST.get("token", "")
    if len(token) > 3 * 1024 * 1024:
        return JsonResponse({"error": "El resultado excede el tamaño permitido."}, status=400)
    try:
        result = signing.loads(token, salt=RESULT_SALT, max_age=900)
    except signing.BadSignature:
        return JsonResponse({"error": "El resultado expiró o no es válido. Analiza otra imagen."}, status=400)
    capture = Capture.objects.create(**result)
    return JsonResponse({"id": capture.pk}, status=201)