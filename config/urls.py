from django.urls import path
from detector import views

urlpatterns = [
    path("", views.index, name="index"),
    path("historial/", views.history, name="history"),
    path("api/detect/", views.detect, name="detect"),
    path("api/save/", views.save, name="save"),
]