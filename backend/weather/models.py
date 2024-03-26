from django.db import models

# Create your models here.
class Entry(models.Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField()

    def __str__(self):
            """String representation of the model."""
            return str(self.id) + ":" + self.name