from django.urls import path

from . import views

urlpatterns = [
    path("api/import", views.employee_import, name="employee-import"),
    path("api/employees", views.employee_list, name="employee-list"),
    path("api/employees/<int:pk>", views.employee_detail, name="employee-detail"),
    path(
        "api/employees/bulk-position",
        views.employee_bulk_position,
        name="employee-bulk-position",
    ),
]
