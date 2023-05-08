from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Card(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    attribute = models.CharField(max_length=50)
    star = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(12),
            MinValueValidator(1),
        ]
    )
    def __str__(self):
        return self.name
