from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from .models import Capture


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
