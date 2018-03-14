from collections import defaultdict
import json

from django.db import models
from model_utils.models import TimeStampedModel


class Zip(TimeStampedModel):
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title
