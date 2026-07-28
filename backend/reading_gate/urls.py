from django.urls import path

from . import views

urlpatterns = [
    path("api/reading/heartbeat", views.reading_heartbeat, name="reading-heartbeat"),
    path("api/test/questions", views.test_questions, name="test-questions"),
    path("api/test/submit", views.test_submit, name="test-submit"),
    path("api/expediente", views.expediente_list, name="expediente-list"),
    path("api/audit", views.audit_list, name="audit-list"),
    path("api/employee/enrollments", views.employee_enrollments, name="employee-enrollments"),
    path(
        "api/admin/assignments/preview",
        views.assignment_preview,
        name="assignment-preview",
    ),
    path(
        "api/admin/assignments",
        views.assignment_apply,
        name="assignment-apply",
    ),
    path(
        "api/admin/enrollments",
        views.admin_enrollments,
        name="admin-enrollments",
    ),
    path(
        "api/admin/enrollments/<int:pk>/<str:action>",
        views.admin_enrollment_action,
        name="admin-enrollment-action",
    ),
]
