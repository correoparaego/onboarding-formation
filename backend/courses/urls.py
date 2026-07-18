from django.urls import path

from . import views

urlpatterns = [
    path("api/courses/", views.course_list_create, name="course-list-create"),
    path("api/courses/<int:pk>/", views.course_detail, name="course-detail"),
    path("api/courses/catalog/", views.course_catalog, name="course-catalog"),
    path("api/banks/", views.question_bank_create, name="question-bank-create"),
]
