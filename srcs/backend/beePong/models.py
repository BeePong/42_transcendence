from django.db import models

# Create your models here.

class Tournament(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    num_players = models.CharField(max_length=100)

    def __str__(self):
        return self.name