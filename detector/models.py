from django.db import models


class Capture(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    detections = models.JSONField(default=list)
    processing_ms = models.PositiveIntegerField()
    image = models.TextField()

    class Meta:
        ordering = ["-created_at", "-id"]
