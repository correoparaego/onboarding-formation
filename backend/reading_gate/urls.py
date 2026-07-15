from django.urls import path

from . import views

urlpatterns = [
    path("api/reading/heartbeat", views.reading_heartbeat, name="reading-heartbeat"),
    path("api/test/questions", views.test_questions, name="test-questions"),
    path("api/test/submit", views.test_submit, name="test-submit"),
    path("api/expediente", views.expediente_list, name="expediente-list"),
]
