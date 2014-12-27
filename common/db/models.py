import uuid
from django.db.models import *

from django.db import models as django_models

from .manager import CommonManager


class Model(django_models.Model):

    objects = CommonManager()

    def as_dict(self):
        output = {}
        for field in self._meta.fields:
            output[field.attname] = field.value_to_string(self)
        return output

    class Meta:
        abstract = True


class UUIDModel(Model):

    id = django_models.UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimestampableModel(Model):

    created = django_models.DateTimeField(auto_now_add=True)
    changed = django_models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
