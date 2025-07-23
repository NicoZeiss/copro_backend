from django.db import models
from django.utils.text import slugify


class Announcement(models.Model):
    url = models.URLField(
        max_length=200,
        unique=True,
        verbose_name='Announcement URL',
    )
    reference = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Announcement Reference',
    )
    department = models.CharField(
        max_length=3,
        verbose_name='Department Code',
    )
    city = models.CharField(
        max_length=100,
        verbose_name='City Name',
    )
    postal_code = models.CharField(
        max_length=5,
        verbose_name='Postal Code',
    )
    condominium_expenses = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Condominium Expenses',
    )

    def __str__(self):
        return f"{self.reference} - {self.city} ({self.postal_code})"
    
    def __repr__(self):
        return f"<Announcement: {str(self)}>"
