from django.urls import path

from . import views

urlpatterns = [
    path("api/ai/key", views.ai_key_set, name="ai-key-set"),
    path("api/ai/key/status", views.ai_key_status, name="ai-key-status"),
    path(
        "api/ai/generate-content",
        views.ai_generate_content,
        name="ai-generate-content",
    ),
    path(
        "api/ai/generate-tests",
        views.ai_generate_tests,
        name="ai-generate-tests",
    ),
]
