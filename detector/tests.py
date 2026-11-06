from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

import cv2
import numpy as np

from django.core import signing
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase

from .models import Capture
from .views import RESULT_SALT
from .vision import analyze


class FoundationTests(TestCase):
    def test_homepage_and_method(self):
        self.assertContains(self.client.get("/"), "OBJECTRA")
        self.assertEqual(self.client.post("/").status_code, 405)

    def test_capture_is_stored_and_ordered(self):
        first = Capture.objects.create(image="first", processing_ms=10)
        latest = Capture.objects.create(
            image="second", processing_ms=20,
            detections=[{"class_id": 63, "name": "Laptop", "confidence": 0.9}],
        )
        self.assertEqual(list(Capture.objects.values_list("id", flat=True)), [latest.id, first.id])
        self.assertEqual(Capture.objects.get(pk=latest.id).detections[0]["name"], "Laptop")

    def test_database_command_checks_real_connection(self):
        output = StringIO()
        call_command("check_database", stdout=output)
        self.assertIn("Conexión comprobada", output.getvalue())


class DetectionFlowTests(TestCase):
    def test_pages_and_http_methods(self):
        self.assertContains(self.client.get("/"), "Explora")
        self.assertContains(self.client.get("/historial/"), "Aún no hay capturas")
        self.assertEqual(self.client.get("/api/detect/").status_code, 405)

    def test_missing_file_and_invalid_confidence(self):
        self.assertEqual(self.client.post("/api/detect/").status_code, 400)
        for confidence in ("nan", "inf", "abc", "0.99"):
            response = self.client.post("/api/detect/", {"frame": SimpleUploadedFile("frame.jpg", b"invalid"), "confidence": confidence})
            self.assertEqual(response.status_code, 400)

    def test_invalid_image_does_not_load_model(self):
        response = self.client.post("/api/detect/", {"frame": SimpleUploadedFile("frame.jpg", b"not an image")})
        self.assertEqual(response.status_code, 400)

    def test_inference_errors_are_explained(self):
        with patch("detector.views.analyze", side_effect=FileNotFoundError("Falta el modelo")):
            response = self.client.post("/api/detect/", {"frame": SimpleUploadedFile("frame.jpg", b"test")})
        self.assertEqual(response.status_code, 503)

    def test_detect_save_and_history(self):
        result = {"detections": [{"class_id": 63, "name": "Laptop", "confidence": 0.9, "area_percent": 12.5}], "processing_ms": 27, "image": "data:image/jpeg;base64,dGVzdA=="}
        with patch("detector.views.analyze", return_value=result):
            response = self.client.post("/api/detect/", {"frame": SimpleUploadedFile("frame.jpg", b"test")})
        self.assertEqual(response.status_code, 200)
        saved = self.client.post("/api/save/", {"token": response.json()["token"]})
        self.assertEqual(saved.status_code, 201)
        self.assertEqual(Capture.objects.get().detections[0]["name"], "Laptop")
        self.assertContains(self.client.get("/historial/"), "Laptop")

    def test_general_objects_are_not_filtered_and_names_have_fallback(self):
        frame = np.zeros((32, 32, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".jpg", frame)
        result = SimpleNamespace(
            names={39: "bottle", 63: "laptop", 67: "cell phone", 4: "airplane"},
            boxes=[SimpleNamespace(cls=np.array(i), conf=np.array(.9), xyxyn=[Mock(cpu=lambda: np.array([.1, .2, .5, .7]))]) for i in (39, 63, 67, 4)],
            masks=None,
            plot=lambda: frame,
        )
        model = Mock()
        model.predict.return_value = [result]
        with patch("detector.vision._model", model):
            response = analyze(encoded.tobytes(), .25)
        self.assertIsNone(model.predict.call_args.kwargs["classes"])
        self.assertEqual([item["name"] for item in response["detections"]], ["Botella", "Laptop", "Celular", "airplane"])
        self.assertTrue(response["image"].startswith("data:image/jpeg;base64,"))

    def test_rejects_unknown_quality(self):
        response = self.client.post("/api/detect/", {"frame": SimpleUploadedFile("frame.jpg", b"test"), "quality": "unknown"})
        self.assertEqual(response.status_code, 400)

    def test_quality_uses_matching_export_resolution(self):
        frame = np.zeros((32, 32, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".jpg", frame)
        model = Mock()
        model.predict.return_value = [SimpleNamespace(names={}, boxes=[], masks=None, plot=lambda: frame)]
        with patch("detector.vision._models", {"balanced": model, "detail": model}):
            for quality, size in (("balanced", 480), ("detail", 640)):
                analyze(encoded.tobytes(), .25, quality)
                self.assertEqual(model.predict.call_args.kwargs["imgsz"], size)

    def test_rejects_modified_and_expired_results(self):
        self.assertEqual(self.client.post("/api/save/", {"token": "inventado"}).status_code, 400)
        token = signing.dumps({}, salt=RESULT_SALT)
        with patch("django.core.signing.time.time", return_value=9999999999):
            self.assertEqual(self.client.post("/api/save/", {"token": token}).status_code, 400)
        self.assertEqual(Capture.objects.count(), 0)

    def test_csrf_is_required(self):
        response = Client(enforce_csrf_checks=True).post("/api/detect/")
        self.assertEqual(response.status_code, 403)

    def test_example_has_no_save_token(self):
        result = {"detections": [], "processing_ms": 1, "image": "data:image/jpeg;base64,dGVzdA=="}
        with patch("detector.views.analyze", return_value=result):
            response = self.client.post("/api/detect/", {"source": "example", "frame": SimpleUploadedFile("sample.jpg", b"test")})
        self.assertFalse(response.json()["can_save"])
        self.assertIsNone(response.json()["token"])
        self.assertEqual(self.client.post("/api/save/", {"token": ""}).status_code, 400)
        self.assertEqual(Capture.objects.count(), 0)

    def test_uploaded_example_is_also_not_saveable(self):
        from django.conf import settings
        data = (settings.BASE_DIR / "static/detector/examples/street.jpg").read_bytes()
        result = {"detections": [], "processing_ms": 1, "image": "data:image/jpeg;base64,dGVzdA=="}
        with patch("detector.views.analyze", return_value=result):
            response = self.client.post("/api/detect/", {"frame": SimpleUploadedFile("renamed.jpg", data)})
        self.assertFalse(response.json()["can_save"])
        self.assertIsNone(response.json()["token"])