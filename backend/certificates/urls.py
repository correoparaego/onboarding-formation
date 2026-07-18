from django.urls import path

from . import views

urlpatterns = [
    path("api/certificate/<int:pk>", views.certificate_pdf, name="certificate-pdf"),
]
