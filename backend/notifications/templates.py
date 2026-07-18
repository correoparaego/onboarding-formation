"""Spanish employee-facing email templates (spec notifications §Spanish Templates).

All employee-facing notifications are in Spanish. The raw token/code is passed in
only to build the magic link and is NEVER written to logs (spec §Delivery Logging).
"""
from django.conf import settings


def _link(token):
    base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
    return f"{base}/acceso?token={token}"


def access_email(employee, token, code):
    link = _link(token)
    subject = "Acceso a tu formación inicial"
    body = (
        f"Hola {employee.name},\n\n"
        f"Tienes asignada una acción formativa. Accede con el siguiente enlace de "
        f"un solo uso:\n\n"
        f"{link}\n\n"
        f"O introduce este código en la pantalla de acceso: {code}\n\n"
        f"El enlace y el código caducan en 24 horas y solo pueden usarse una vez.\n\n"
        f"Si no esperabas este mensaje, ignóralo.\n\n"
        f"Equipo de Formación"
    )
    return subject, body


def reminder_email(employee, token, code):
    link = _link(token)
    subject = "Recordatorio: completa tu formación inicial"
    body = (
        f"Hola {employee.name},\n\n"
        f"Te recordamos que tienes una acción formativa pendiente. Accede aquí:\n\n"
        f"{link}\n\n"
        f"Código de acceso: {code}\n\n"
        f"Equipo de Formación"
    )
    return subject, body


def completion_email(employee, course_title):
    subject = "Has completado tu formación inicial"
    body = (
        f"Hola {employee.name},\n\n"
        f"¡Enhorabuena! Has superado la formación: «{course_title}».\n\n"
        f"Puedes solicitar tu certificado desde la aplicación.\n\n"
        f"Equipo de Formación"
    )
    return subject, body
