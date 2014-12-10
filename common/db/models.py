from django.db.models import *

from django.db import models as django_models


class TimestampableModel(django_models.Model):

    created = django_models.DateTimeField(auto_now_add=True)
    changed = django_models.DateTimeField(auto_now=True)
