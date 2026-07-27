"""URL configuration for the MVP Formación Inicial project.

PR1 only scaffolds the project. Admin is mounted; the JSON API is introduced
in later phases (auth, import, courses, reading gate, ...).
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.generic import TemplateView


def api_health(request):
    return JsonResponse({"status": "ok", "service": "mvp-formacion-inicial"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", api_health, name="api-health"),
    path("", include("authentication.urls")),
    path("", include("employees.urls")),
    path("", include("courses.urls")),
    path("", include("ai_generation.urls")),
    path("", include("reading_gate.urls")),
    path("", include("notifications.urls")),
    path("", include("certificates.urls")),
    # Catch-all para servir frontend SPA (debe estar al final)
    re_path(r'^(?!api/|admin/|static/|media/).*$', 
            TemplateView.as_view(template_name='index.html')),
]
