from django.db.models import *


class TimestampableModel(Model):

    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
