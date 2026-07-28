from django.urls import path

from . import views

urlpatterns = [
    path("api/courses/", views.course_list_create, name="course-list-create"),
    path("api/courses/<int:pk>/", views.course_detail, name="course-detail"),
    path("api/courses/<int:pk>/draft/", views.course_draft, name="course-draft"),
    path(
        "api/course-versions/<int:pk>/",
        views.course_version_detail,
        name="course-version-detail",
    ),
    path(
        "api/course-versions/<int:pk>/publish/",
        views.course_version_publish,
        name="course-version-publish",
    ),
    path("api/positions/", views.position_list, name="position-list"),
    path("api/sections/<int:pk>/pdf/", views.section_pdf, name="section-pdf"),
    path("api/courses/catalog/", views.course_catalog, name="course-catalog"),
    path("api/banks/", views.question_bank_create, name="question-bank-create"),
]
