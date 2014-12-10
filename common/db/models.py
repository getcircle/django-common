import uuid
from django.db.models import *

from django.db import models as django_models


class UUIDModel(django_models.Model):

    id = django_models.UUIDField(primary_key=True, default=uuid.uuid4)


class TimestampableModel(django_models.Model):

    created = django_models.DateTimeField(auto_now_add=True)
    changed = django_models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
