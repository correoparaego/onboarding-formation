from django.db import migrations


def seed_badges(apps, schema_editor):
    Badge = apps.get_model("certificates", "Badge")
    initial = [
        ("primer-curso", "Primer curso"),
        ("catalogo-completo", "Catálogo completo"),
        ("sin-fallos", "Sin fallos"),
    ]
    for slug, label in initial:
        Badge.objects.get_or_create(slug=slug, defaults={"label": label})


def revert_badges(apps, schema_editor):
    Badge = apps.get_model("certificates", "Badge")
    Badge.objects.filter(
        slug__in=["primer-curso", "catalogo-completo", "sin-fallos"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("certificates", "0002_certificate"),
    ]

    operations = [
        migrations.RunPython(seed_badges, revert_badges),
    ]
