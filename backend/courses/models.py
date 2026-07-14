from django.core.exceptions import ValidationError
from django.db import models


class Position(models.Model):
    """Catalog key linking job positions to mandatory courses.

    The design references ``position_catalog (M2M Position->Course)``; this model
    makes that implicit ``Position`` explicit so the catalog M2M has a concrete
    target. Employee.position (verbatim imported label) is reconciled to this
    slug/name in later phases.
    """

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "positions"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify

            self.slug = slugify(self.name) or self.name.lower().replace(" ", "-")
        super().save(*args, **kwargs)


class Course(models.Model):
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to="courses/pdfs/", null=True, blank=True)
    # min_time_divisor: minTimePerSection = section_base / min_time_divisor.
    min_time_divisor = models.PositiveIntegerField(default=3)
    position_catalog = models.ManyToManyField(
        Position, related_name="courses", blank=True
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="sections"
    )
    order = models.PositiveIntegerField()
    # Estimated base reading time for this section, in seconds.
    section_base = models.PositiveIntegerField(help_text="Base reading time (seconds)")

    class Meta:
        ordering = ["course", "order"]
        unique_together = [("course", "order")]

    def __str__(self):
        return f"{self.course.title} / section {self.order}"


class QuestionBank(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="banks"
    )

    class Meta:
        verbose_name_plural = "question banks"

    def __str__(self):
        return f"Bank for {self.course.title}"


class Question(models.Model):
    bank = models.ForeignKey(
        QuestionBank, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.TextField()
    options = models.JSONField(help_text="Ordered list of option strings")
    # Single correct answer: index into ``options``. Enforced in clean()/save().
    correct_index = models.PositiveSmallIntegerField()

    def clean(self):
        super().clean()
        if not isinstance(self.options, list) or len(self.options) < 2:
            raise ValidationError({"options": "At least two options are required."})
        if not (0 <= self.correct_index < len(self.options)):
            raise ValidationError(
                {"correct_index": "correct_index must point to a valid option."}
            )

    def save(self, *args, **kwargs):
        self.full_clean(exclude=None, validate_unique=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Q{bank_id}: {self.text[:40]}"
