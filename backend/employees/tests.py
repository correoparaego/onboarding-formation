from django.contrib.auth import get_user_model
from django.test import TestCase

from courses.models import Position
from employees.models import Employee


class EmployeePositionManagementTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            "position-admin", "admin@example.com", "pw", is_staff=True
        )
        self.old_position = Position.objects.create(name="Operario")
        self.new_position = Position.objects.create(name="Supervisor")
        self.employees = [
            Employee.objects.create(
                dni=f"1234567{index}Z",
                name=f"Empleado {index}",
                position="Operario",
                current_position=self.old_position,
                email=f"employee{index}@example.com",
            )
            for index in range(2)
        ]

    def test_employee_routes_require_admin(self):
        self.assertEqual(self.client.get("/api/employees").status_code, 403)

    def test_individual_position_change_preserves_imported_label(self):
        self.client.force_login(self.admin)
        response = self.client.patch(
            f"/api/employees/{self.employees[0].id}",
            data={"position_id": self.new_position.id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.employees[0].refresh_from_db()
        self.assertEqual(self.employees[0].position, "Operario")
        self.assertEqual(self.employees[0].current_position, self.new_position)

    def test_bulk_position_change(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            "/api/employees/bulk-position",
            data={
                "employee_ids": [employee.id for employee in self.employees],
                "position_id": self.new_position.id,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["updated"], 2)
        self.assertEqual(
            Employee.objects.filter(current_position=self.new_position).count(), 2
        )
