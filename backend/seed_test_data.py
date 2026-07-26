"""
Comprehensive seed script for testing the onboarding formation platform.

Creates: admin user, positions, courses (with PDFs), question banks, employees,
enrollments, access tokens, reading progress, expedientes, and certificates.

Idempotent — safe to run multiple times.

Usage:
    cd backend
    python seed_test_data.py
"""
import io
import os
import sys
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mvp_project.settings")

import django
django.setup()

import pandas as pd
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone

from courses.models import Position, Course, Section, QuestionBank, Question
from employees.models import Employee
from reading_gate.models import Enrollment, ReadingProgress, AuditEvent, Expediente
from reading_gate.services import assign_mandatory_courses
from authentication.models import EmployeeAccessToken
from certificates.models import Badge, EmployeeBadge, Certificate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_minimal_pdf(title: str) -> bytes:
    """Generate a minimal valid 1-page PDF with the given title using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as rl_canvas
        buf = io.BytesIO()
        c = rl_canvas.Canvas(buf, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 60, title)
        c.setFont("Helvetica", 11)
        c.drawString(50, height - 100, "Contenido de ejemplo para pruebas de la plataforma de formacion.")
        c.drawString(50, height - 120, "Este documento ha sido generado automaticamente como dato de prueba.")
        c.showPage()
        c.save()
        return buf.getvalue()
    except ImportError:
        # Fallback: hand-crafted minimal PDF (no reportlab needed)
        content = f"BT /F1 18 Tf 100 700 Td ({title}) Tj ET"
        pdf = (
            b"%PDF-1.0\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>/Contents 4 0 R>>endobj\n"
            b"4 0 obj<</Length " + str(len(content)).encode() + b">>\nstream\n" + content.encode() + b"\nendstream\nendobj\n"
            b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000317 00000 n \n"
            b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n420\n%%EOF"
        )
        return pdf


def valid_dni_for_index(index: int) -> str:
    """Generate a structurally valid Spanish DNI for a given index (0-based)."""
    letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    number = 10000000 + index
    letter = letters[number % 23]
    return f"{number}{letter}"


# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

POSITIONS = [
    {"name": "Operario", "slug": "operario"},
    {"name": "Tecnico", "slug": "tecnico"},
    {"name": "Supervisor", "slug": "supervisor"},
]

COURSES_DATA = [
    {
        "title": "Seguridad en el Trabajo",
        "min_time_divisor": 3,
        "positions": ["Operario", "Tecnico"],
        "sections": [
            {"order": 1, "section_base": 120},
            {"order": 2, "section_base": 180},
            {"order": 3, "section_base": 150},
        ],
    },
    {
        "title": "Prevencion de Riesgos Laborales",
        "min_time_divisor": 4,
        "positions": ["Operario", "Tecnico", "Supervisor"],
        "sections": [
            {"order": 1, "section_base": 200},
            {"order": 2, "section_base": 250},
            {"order": 3, "section_base": 180},
        ],
    },
    {
        "title": "Gestion de Equipos",
        "min_time_divisor": 3,
        "positions": ["Supervisor"],
        "sections": [
            {"order": 1, "section_base": 300},
            {"order": 2, "section_base": 240},
            {"order": 3, "section_base": 180},
            {"order": 4, "section_base": 200},
        ],
    },
    {
        "title": "Normativa ISO 9001",
        "min_time_divisor": 5,
        "positions": ["Tecnico", "Supervisor"],
        "sections": [
            {"order": 1, "section_base": 180},
            {"order": 2, "section_base": 220},
            {"order": 3, "section_base": 160},
        ],
    },
]

QUESTIONS_DATA = {
    "Seguridad en el Trabajo": [
        {
            "text": "Cual es el equipo de proteccion personal basico para trabajar en almacen?",
            "options": ["Casco y botas de seguridad", "Solo guantes de latex", "Gafas de sol", "Ropa casual"],
            "correct_index": 0,
        },
        {
            "text": "Que debe hacer si detecta un derrame de producto quimico?",
            "options": ["Ignorarlo", "Evacuar y avisar al responsable", "Limpiarlo con agua", "Taparlo con carton"],
            "correct_index": 1,
        },
        {
            "text": "Cual es la senal de seguridad de color rojo?",
            "options": ["Obligacion", "Peligro o prohibicion", "Informacion", "Auxilio"],
            "correct_index": 1,
        },
        {
            "text": "Cada cuanto tiempo se debe realizar una revision de extintores?",
            "options": ["Cada 5 anos", "Cada mes visual y anual completa", "Solo cuando se usa", "Nunca"],
            "correct_index": 1,
        },
        {
            "text": "Que indica una senal triangular con borde rojo?",
            "options": ["Prohibicion", "Obligacion", "Advertencia de peligro", "Salida de emergencia"],
            "correct_index": 2,
        },
    ],
    "Prevencion de Riesgos Laborales": [
        {
            "text": "Que ley regula la prevencion de riesgos laborales en Espana?",
            "options": ["Ley 31/1995", "Ley Orgánica 3/2018", "Real Decreto 486/1997", "Ley 54/2003"],
            "correct_index": 0,
        },
        {
            "text": "Cual es la obligacion principal del empresario en PRL?",
            "options": ["Solo proporcionar EPIs", "Proteger la seguridad y salud de los trabajadores", "Firmar papeles", "Contratar un seguro"],
            "correct_index": 1,
        },
        {
            "text": "Que es un riesgo laboral?",
            "options": ["Una posibilidad de dano derivado del trabajo", "Un tipo de contrato", "Una sancion", "Un beneficio fiscal"],
            "correct_index": 0,
        },
        {
            "text": "Cuantos delegados de prevencion tiene derecho a elegir un centro de 50 trabajadores?",
            "options": ["1", "2", "3", "4"],
            "correct_index": 2,
        },
        {
            "text": "Que documento recoge la evaluacion de riesgos?",
            "options": ["El plan de prevencion de riesgos laborales", "El contrato de trabajo", "La nomina", "El manual de empleado"],
            "correct_index": 0,
        },
    ],
    "Gestion de Equipos": [
        {
            "text": "Cual es la clave principal para una comunicacion efectiva en equipo?",
            "options": ["Hablar mas", "Escucha activa", "Enviar correos", "Reuniones diarias"],
            "correct_index": 1,
        },
        {
            "text": "Que modelo se usa para establecer objetivos claros?",
            "options": ["SMART", "SWOT", "PEST", "Gantt"],
            "correct_index": 0,
        },
        {
            "text": "Que es el feedback constructivo?",
            "options": ["Critica destructiva", "Retroalimentacion orientada a la mejora", "Un castigo", "Una recompensa"],
            "correct_index": 1,
        },
        {
            "text": "Cual es la mejor forma de resolver un conflicto en el equipo?",
            "options": ["Ignorarlo", "Imponer la decision del jefe", "Dialogo abierto y mediacion", "Cambiar de equipo"],
            "correct_index": 2,
        },
        {
            "text": "Que caracteriza a un equipo de alto rendimiento?",
            "options": ["Trabajan solos", "Confianza, objetivos claros y comunicacion", "Muchas reuniones", "Jerarquia estricta"],
            "correct_index": 1,
        },
    ],
    "Normativa ISO 9001": [
        {
            "text": "Que es la norma ISO 9001?",
            "options": ["Norma de seguridad informatica", "Norma de gestion de calidad", "Norma medioambiental", "Norma de seguridad alimentaria"],
            "correct_index": 1,
        },
        {
            "text": "Cual es el principio basico de la mejora continua?",
            "options": ["Ciclo PDCA (Plan-Do-Check-Act)", "Ciclo de vida del producto", "Analisis FODA", "Diagrama de Ishikawa"],
            "correct_index": 0,
        },
        {
            "text": "Que documento describe el sistema de gestion de calidad?",
            "options": ["Manual de calidad", "Factura", "Contrato", "Nomina"],
            "correct_index": 0,
        },
        {
            "text": "Cada cuanto se realiza una auditoria interna de ISO 9001?",
            "options": ["Cada 5 anos", "Periodicamente segun plan", "Solo al inicio", "Nunca"],
            "correct_index": 1,
        },
        {
            "text": "Que es una no conformidad en ISO 9001?",
            "options": ["Un incumplimiento de un requisito", "Una mejora", "Un objetivo", "Un cliente nuevo"],
            "correct_index": 0,
        },
    ],
}

EMPLOYEES_DATA = [
    {"name": "Juan Perez", "position": "Operario", "email": "juan.perez@test.local", "phone": "+34600100001"},
    {"name": "Maria Garcia", "position": "Tecnico", "email": "maria.garcia@test.local", "phone": "+34600100002"},
    {"name": "Carlos Lopez", "position": "Operario", "email": "carlos.lopez@test.local", "phone": "+34600100003"},
    {"name": "Ana Martinez", "position": "Supervisor", "email": "ana.martinez@test.local", "phone": "+34600100004"},
    {"name": "Pedro Sanchez", "position": "Tecnico", "email": "pedro.sanchez@test.local", "phone": "+34600100005"},
    {"name": "Laura Fernandez", "position": "Operario", "email": "laura.fernandez@test.local", "phone": "+34600100006"},
    {"name": "David Rodriguez", "position": "Supervisor", "email": "david.rodriguez@test.local", "phone": "+34600100007"},
    {"name": "Sofia Gonzalez", "position": "Tecnico", "email": "sofia.gonzalez@test.local", "phone": "+34600100008"},
    {"name": "Javier Diaz", "position": "Operario", "email": "javier.diaz@test.local", "phone": "+34600100009"},
    {"name": "Elena Moreno", "position": "Supervisor", "email": "elena.moreno@test.local", "phone": "+34600100010"},
    {"name": "Miguel Alvarez", "position": "Operario", "email": "miguel.alvarez@test.local", "phone": "+34600100011"},
    {"name": "Carmen Ruiz", "position": "Tecnico", "email": "carmen.ruiz@test.local", "phone": "+34600100012"},
    {"name": "Francisco Torres", "position": "Operario", "email": "francisco.torres@test.local", "phone": "+34600100013"},
    {"name": "Isabel Navarro", "position": "Supervisor", "email": "isabel.navarro@test.local", "phone": "+34600100014"},
    {"name": "Roberto Molina", "position": "Tecnico", "email": "roberto.molina@test.local", "phone": "+34600100015"},
]


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

def seed_admin():
    print("\n--- Admin user ---")
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={"email": "admin@test.local", "is_staff": True, "is_superuser": True},
    )
    if created:
        admin_user.set_password("admin1234")
        admin_user.save()
        print("[OK] Admin created: admin / admin1234")
    else:
        print("[--] Admin already exists")
    return admin_user


def seed_positions():
    print("\n--- Positions ---")
    positions = {}
    for p in POSITIONS:
        pos, created = Position.objects.get_or_create(slug=p["slug"], defaults={"name": p["name"]})
        positions[p["name"]] = pos
        tag = "[OK]" if created else "[--]"
        print(f"{tag} {pos.name}")
    return positions


def seed_courses():
    print("\n--- Courses ---")
    courses = {}
    for cd in COURSES_DATA:
        course, created = Course.objects.get_or_create(
            title=cd["title"],
            defaults={"min_time_divisor": cd["min_time_divisor"]},
        )
        if created:
            # Attach PDF
            pdf_bytes = make_minimal_pdf(cd["title"])
            fname = cd["title"].lower().replace(" ", "_") + ".pdf"
            course.pdf_file.save(fname, ContentFile(pdf_bytes), save=True)

            # Sections
            for s in cd["sections"]:
                Section.objects.get_or_create(course=course, order=s["order"], defaults={"section_base": s["section_base"]})

            # Position catalog
            for pname in cd["positions"]:
                pos = Position.objects.filter(name__iexact=pname).first()
                if pos:
                    course.position_catalog.add(pos)

            print(f"[OK] {course.title} (id={course.id}, pdf={bool(course.pdf_file)})")
        else:
            print(f"[--] {course.title} already exists (id={course.id})")
        courses[cd["title"]] = course
    return courses


def seed_question_banks(courses):
    print("\n--- Question banks ---")
    for title, questions in QUESTIONS_DATA.items():
        course = courses.get(title)
        if not course:
            print(f"[!!] No course found for: {title}")
            continue
        bank, created = QuestionBank.objects.get_or_create(course=course)
        if created or bank.questions.count() == 0:
            for qd in questions:
                existing = bank.questions.filter(text=qd["text"]).exists()
                if not existing:
                    Question.objects.create(
                        bank=bank,
                        text=qd["text"],
                        options=qd["options"],
                        correct_index=qd["correct_index"],
                    )
            print(f"[OK] Bank for '{title}': {bank.questions.count()} questions")
        else:
            print(f"[--] Bank for '{title}' already has {bank.questions.count()} questions")


def seed_employees():
    print("\n--- Employees ---")
    from django.db import connection
    import hashlib

    employees = []
    for i, ed in enumerate(EMPLOYEES_DATA):
        dni = valid_dni_for_index(i)

        # Check if employee already exists by dni_lookup hash
        dni_hash = hashlib.sha256(dni.encode()).hexdigest()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM employees_employee WHERE dni_lookup = %s", [dni_hash]
            )
            existing_id = cursor.fetchone()

        if existing_id:
            emp = Employee.objects.get(id=existing_id[0])
            print(f"[--] {emp.name} (DNI={dni}, pos={emp.position})")
        else:
            # Create via raw SQL to populate dni_lookup (not in current model)
            from common.crypto import encrypt_value
            encrypted_dni = encrypt_value(dni)
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO employees_employee (dni, dni_lookup, name, position, email, phone)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    [encrypted_dni, dni_hash, ed["name"], ed["position"], ed["email"], ed["phone"]],
                )
                emp_id = cursor.lastrowid
            emp = Employee.objects.get(id=emp_id)
            print(f"[OK] {emp.name} (DNI={dni}, pos={emp.position})")

        employees.append(emp)
    return employees


def generate_excel(employees):
    print("\n--- Excel file ---")
    rows = []
    for i, emp in enumerate(employees):
        rows.append({
            "dni": valid_dni_for_index(i),
            "name": emp.name,
            "position": emp.position,
            "email": emp.email,
            "phone": emp.phone,
        })
    df = pd.DataFrame(rows)
    path = "test_employees.xlsx"
    df.to_excel(path, index=False)
    print(f"[OK] {path} written ({len(rows)} rows)")
    return path


def seed_enrollments(employees):
    print("\n--- Enrollments (via assign_mandatory_courses) ---")
    total_new = 0
    for emp in employees:
        n = assign_mandatory_courses(emp)
        total_new += n
    print(f"[OK] {total_new} new enrollments created")
    return Enrollment.objects.filter(employee__in=employees)


def seed_access_tokens(enrollments):
    print("\n--- Access tokens ---")
    # assign_mandatory_courses already issues tokens via notifications.services.
    # We collect existing unconsumed tokens for the first 5 enrollments so the
    # tester has the raw values. Since raw values are never stored (only hashes),
    # we issue FRESH tokens for display purposes (marking old ones consumed).
    tokens_issued = []
    for enrollment in enrollments[:5]:
        # Consume any existing unconsumed tokens so we start clean
        now = timezone.now()
        EmployeeAccessToken.objects.filter(
            enrollment=enrollment, consumed_at__isnull=True
        ).update(consumed_at=now)

        instance, raw_token, code = EmployeeAccessToken.issue(enrollment.employee, enrollment=enrollment)
        tokens_issued.append({
            "employee": enrollment.employee.name,
            "course": enrollment.course.title,
            "token": raw_token,
            "code": code,
            "enrollment_id": enrollment.id,
        })
        print(f"[OK] Token for {enrollment.employee.name} / {enrollment.course.title}")
    return tokens_issued


def seed_reading_progress(enrollments):
    print("\n--- Reading progress (partial) ---")
    # Give partial progress to some enrollments
    count = 0
    for enrollment in enrollments[5:10]:
        sections = list(enrollment.course.sections.order_by("order"))
        if not sections:
            continue
        # Complete first section partially
        section = sections[0]
        min_time = max(1, section.section_base // max(1, enrollment.course.min_time_divisor))
        partial_time = min_time // 2  # half done
        _, created = ReadingProgress.objects.get_or_create(
            enrollment=enrollment,
            section=section,
            defaults={
                "accumulated_time": partial_time,
                "reached_section": 1,
                "device_id": "seed-device-001",
                "session_id": "seed-session-001",
            },
        )
        if created:
            count += 1
            enrollment.status = "in_progress"
            enrollment.save(update_fields=["status"])
    print(f"[OK] {count} reading progress records created")


def seed_expedientes(enrollments):
    print("\n--- Expedientes ---")
    passed_enrollments = enrollments[0:2]
    in_progress_enrollments = enrollments[2:4]

    count = 0
    for enrollment in passed_enrollments:
        enrollment.status = "passed"
        enrollment.attempts_used = 1
        enrollment.save(update_fields=["status", "attempts_used"])
        _, created = Expediente.objects.get_or_create(
            enrollment=enrollment,
            defaults={
                "employee": enrollment.employee,
                "course": enrollment.course,
                "status": "passed",
                "attempts_used": 1,
                "score": 5,
                "total": 5,
                "completed_at": timezone.now(),
            },
        )
        if created:
            count += 1

    for enrollment in in_progress_enrollments:
        enrollment.status = "in_progress"
        enrollment.attempts_used = 1
        enrollment.save(update_fields=["status", "attempts_used"])
        _, created = Expediente.objects.get_or_create(
            enrollment=enrollment,
            defaults={
                "employee": enrollment.employee,
                "course": enrollment.course,
                "status": "in_progress",
                "attempts_used": 1,
            },
        )
        if created:
            count += 1

    print(f"[OK] {count} expediente records created")
    return passed_enrollments


def seed_certificates(passed_enrollments):
    print("\n--- Certificates ---")
    count = 0
    for enrollment in passed_enrollments:
        _, created = Certificate.objects.get_or_create(
            enrollment=enrollment,
            defaults={"core_fields_hash": "seed-hash"},
        )
        if created:
            count += 1
    print(f"[OK] {count} certificate records created")


def seed_badges():
    print("\n--- Badges ---")
    from certificates.services import ensure_badges
    created = ensure_badges()
    if created:
        print(f"[OK] Badges created: {', '.join(created)}")
    else:
        print("[--] Badges already exist")


def print_summary(tokens_issued, courses, enrollments):
    print("\n" + "=" * 70)
    print("  SEED COMPLETE — Summary")
    print("=" * 70)

    print("\n  Admin credentials:")
    print("    username: admin")
    print("    password: admin1234")

    print("\n  Courses:")
    for title, course in courses.items():
        print(f"    [{course.id}] {title} (positions: {', '.join(p.name for p in course.position_catalog.all())})")

    print(f"\n  Employees: {Employee.objects.count()}")
    print(f"  Enrollments: {Enrollment.objects.count()}")

    status_counts = {}
    for e in Enrollment.objects.all():
        status_counts[e.status] = status_counts.get(e.status, 0) + 1
    print(f"  Enrollment status distribution: {status_counts}")

    if tokens_issued:
        print("\n  Employee access tokens (for testing redeem flow):")
        print(f"  {'Employee':<25} {'Course':<35} {'Token':<50} {'Code':<12}")
        print("  " + "-" * 122)
        for t in tokens_issued:
            print(f"  {t['employee']:<25} {t['course']:<35} {t['token']:<50} {t['code']:<12}")

    print("\n  Excel file: test_employees.xlsx")
    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n=== Seeding test data for onboarding formation platform ===\n")

    seed_admin()
    positions = seed_positions()
    courses = seed_courses()
    seed_question_banks(courses)
    employees = seed_employees()
    generate_excel(employees)
    enrollments = seed_enrollments(employees)
    tokens_issued = seed_access_tokens(enrollments)
    seed_reading_progress(enrollments)
    passed_enrollments = seed_expedientes(enrollments)
    seed_certificates(passed_enrollments)
    seed_badges()
    print_summary(tokens_issued, courses, enrollments)

    print("\n=== Done ===\n")
