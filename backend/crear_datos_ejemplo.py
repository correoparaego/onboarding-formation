"""
Script para generar datos de ejemplo para la aplicación de formación.
Genera:
1. Archivo Excel con empleados de ejemplo
2. Posiciones y cursos de ejemplo en la base de datos
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mvp_project.settings")
django.setup()

import pandas as pd
from django.contrib.auth.models import User
from courses.models import Position, Course, Section
from employees.models import Employee

def create_excel_example():
    """Crea un archivo Excel de ejemplo con empleados."""
    data = {
        "dni": [
            "12345678A", "87654321B", "11223344C", "44556677D", "99887766E",
            "55443322F", "66778899G", "33221100H", "77889900I", "22334455J"
        ],
        "name": [
            "Juan Pérez", "María García", "Carlos López", "Ana Martínez", "Pedro Sánchez",
            "Laura Fernández", "David Rodríguez", "Sofía González", "Javier Díaz", "Elena Moreno"
        ],
        "position": [
            "Operario", "Técnico", "Operario", "Supervisor", "Técnico",
            "Operario", "Técnico", "Supervisor", "Operario", "Técnico"
        ],
        "email": [
            "juan@empresa.com", "maria@empresa.com", "carlos@empresa.com", "ana@empresa.com",
            "pedro@empresa.com", "laura@empresa.com", "david@empresa.com", "sofia@empresa.com",
            "javier@empresa.com", "elena@empresa.com"
        ],
        "phone": [
            "+34600111222", "+34600333444", "+34600555666", "+34600777888", "+34600999000",
            "+34600111333", "+34600222444", "+34600333555", "+34600444666", "+34600555777"
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel("empleados_ejemplo.xlsx", index=False)
    print("[OK] Archivo empleados_ejemplo.xlsx creado")

def create_positions():
    """Crea posiciones de ejemplo."""
    positions = [
        {"name": "Operario", "slug": "operario"},
        {"name": "Técnico", "slug": "tecnico"},
        {"name": "Supervisor", "slug": "supervisor"},
    ]
    
    created = 0
    for pos_data in positions:
        pos, was_created = Position.objects.get_or_create(
            slug=pos_data["slug"],
            defaults={"name": pos_data["name"]}
        )
        if was_created:
            created += 1
            print(f"[OK] Posicion creada: {pos.name}")
    
    print(f"[OK] {created} posiciones nuevas creadas")

def create_courses():
    """Crea cursos de ejemplo."""
    courses_data = [
        {
            "title": "Seguridad en el Trabajo",
            "min_time_divisor": 3,
            "positions": ["Operario", "Técnico"],
            "sections": [
                {"order": 1, "section_base": 120},
                {"order": 2, "section_base": 180},
                {"order": 3, "section_base": 150},
            ]
        },
        {
            "title": "Prevención de Riesgos Laborales",
            "min_time_divisor": 4,
            "positions": ["Operario", "Técnico", "Supervisor"],
            "sections": [
                {"order": 1, "section_base": 200},
                {"order": 2, "section_base": 250},
            ]
        },
        {
            "title": "Gestión de Equipos",
            "min_time_divisor": 3,
            "positions": ["Supervisor"],
            "sections": [
                {"order": 1, "section_base": 300},
                {"order": 2, "section_base": 240},
                {"order": 3, "section_base": 180},
                {"order": 4, "section_base": 200},
            ]
        },
        {
            "title": "Normativa ISO 9001",
            "min_time_divisor": 5,
            "positions": ["Técnico", "Supervisor"],
            "sections": [
                {"order": 1, "section_base": 180},
                {"order": 2, "section_base": 220},
            ]
        },
    ]
    
    created = 0
    for course_data in courses_data:
        course, was_created = Course.objects.get_or_create(
            title=course_data["title"],
            defaults={"min_time_divisor": course_data["min_time_divisor"]}
        )
        
        if was_created:
            created += 1
            print(f"[OK] Curso creado: {course.title}")
            
            # Crear secciones
            for section_data in course_data["sections"]:
                Section.objects.create(
                    course=course,
                    order=section_data["order"],
                    section_base=section_data["section_base"]
                )
            
            # Asignar posiciones
            for pos_name in course_data["positions"]:
                try:
                    pos = Position.objects.get(name=pos_name)
                    course.position_catalog.add(pos)
                except Position.DoesNotExist:
                    print(f"  [WARN] Posicion no encontrada: {pos_name}")
    
    print(f"[OK] {created} cursos nuevos creados")

if __name__ == "__main__":
    print("\n=== Generando datos de ejemplo ===\n")
    
    print("1. Creando archivo Excel...")
    create_excel_example()
    
    print("\n2. Creando posiciones...")
    create_positions()
    
    print("\n3. Creando cursos...")
    create_courses()
    
    print("\n=== Datos de ejemplo generados ===")
    print("\nPróximos pasos:")
    print("1. Importa empleados_ejemplo.xlsx desde /admin/import")
    print("2. Los empleados se matricularán automáticamente en sus cursos obligatorios")
    print("3. Genera tokens de acceso desde el panel de administración")
