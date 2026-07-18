from django.urls import path

from . import views

urlpatterns = [
    path(
        "api/admin/enrollment/<int:pk>/resend-access",
        views.admin_resend_access,
        name="admin-resend-access",
    ),
]
