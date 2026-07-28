from django.urls import path

from . import views

urlpatterns = [
    path(
        "api/admin/access-codes/batch",
        views.admin_batch_access,
        name="admin-batch-access",
    ),
    path(
        "api/admin/enrollment/<int:pk>/resend-access",
        views.admin_resend_access,
        name="admin-resend-access",
    ),
]
