from django.urls import path

from . import views

urlpatterns = [
    path("api/auth/admin/login", views.admin_login, name="admin-login"),
    path("api/auth/admin/logout", views.admin_logout, name="admin-logout"),
    path(
        "api/auth/employee/redeem",
        views.employee_redeem,
        name="employee-redeem",
    ),
]
