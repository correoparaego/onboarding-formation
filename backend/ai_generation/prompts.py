"""Prompt builders (design §PII Guard).

These functions build LLM prompts from COURSE-ONLY material: the course title,
the admin's guided answers, uploaded reference documents, or extracted PDF
text. They never receive an Employee record. As defense-in-depth, every input
is passed through the PII-exclusion sanitizer so accidental employee PII in
reference material is stripped before any provider call.
"""
from .sanitizer import sanitize_many, sanitize_text

_SYSTEM = (
    "Eres un asistente de redacción de cursos de formación. Responde SOLO con "
    "JSON válido, sin texto adicional. No incluyas datos personales de "
    "empleados (DNI, nombre, email, teléfono)."
)


def build_content_prompt(course_title: str, answers: dict, reference_docs=None):
    """Mode A — guided course content from admin answers + reference docs."""
    reference_docs = reference_docs or []
    parts = [f"Título del curso: {course_title}"]
    for question, answer in (answers or {}).items():
        parts.append(f"Pregunta: {question}\nRespuesta: {answer}")
    for i, doc in enumerate(reference_docs, start=1):
        parts.append(f"Documento de referencia {i}:\n{doc}")
    user_text = sanitize_text(
        "Genera un borrador de curso en JSON con claves 'title' y 'sections' "
        "(cada sección: order, title, content, section_base en segundos).\n\n"
        + "\n\n".join(parts)
    )
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_text},
    ]


def build_test_prompt(pdf_text: str):
    """Mode B — comprehension test from extracted PDF text."""
    user_text = sanitize_text(
        "Genera un test de evaluación en JSON con clave 'questions'. Cada "
        "pregunta: text, options (lista), correct_index (un solo entero). "
        "Exactamente una respuesta correcta por pregunta.\n\n"
        f"Texto extraído del PDF:\n{pdf_text}"
    )
    return [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_text},
    ]
