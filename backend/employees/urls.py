from django.urls import path

from . import views

urlpatterns = [
    path("api/import", views.employee_import, name="employee-import"),
    path("api/employees", views.employee_list, name="employee-list"),
]
