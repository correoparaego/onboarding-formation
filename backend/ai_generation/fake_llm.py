"""
Fake LLM responses for testing.
Returns deterministic course content and test questions without external API calls.
"""


def fake_generate_course_content(course_title: str, answers: dict, reference_docs: list) -> dict:
    """Generate fake course draft for testing."""
    return {
        "title": course_title,
        "sections": [
            {
                "order": 1,
                "title": f"Introduccion a {course_title}",
                "content": f"Contenido de introduccion para {course_title}.",
                "section_base": 120,
            },
            {
                "order": 2,
                "title": f"Conceptos clave de {course_title}",
                "content": "Conceptos fundamentales y mejores practicas.",
                "section_base": 180,
            },
            {
                "order": 3,
                "title": "Aplicacion practica",
                "content": "Ejemplos reales y casos de uso.",
                "section_base": 150,
            },
        ],
    }


def fake_generate_test_questions(pdf_text: str, course_title: str) -> dict:
    """Generate fake test questions for testing."""
    return {
        "questions": [
            {
                "text": f"Cual es el objetivo principal de {course_title}?",
                "options": [
                    "Mejorar la seguridad laboral",
                    "Aumentar la productividad",
                    "Reducir costes",
                    "Cumplir normativas",
                ],
                "correct_index": 0,
            },
            {
                "text": f"Que aspecto es mas importante en {course_title}?",
                "options": [
                    "Teoria",
                    "Practica",
                    "Documentacion",
                    "Evaluacion",
                ],
                "correct_index": 1,
            },
            {
                "text": f"Cuando se aplica {course_title}?",
                "options": [
                    "Solo en emergencias",
                    "Diariamente",
                    "Semanalmente",
                    "Nunca",
                ],
                "correct_index": 1,
            },
        ]
    }
