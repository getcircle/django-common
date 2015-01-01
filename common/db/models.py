import uuid
from django.db.models import *
from django.db import models as django_models
from protobuf_to_dict import dict_to_protobuf

from .manager import CommonManager


class Null(object):
    pass


class Model(django_models.Model):

    objects = CommonManager()

    def as_dict(self):
        output = {}
        for field in self._meta.fields:
            value = field.value_from_object(self)
            if not isinstance(value, (bool,)):
                value = field.value_to_string(self)
            output[field.attname] = value
        return output

    def to_protobuf(self, protobuf, strict=False, **overrides):
        model = self.as_dict()
        model.update(overrides)
        return dict_to_protobuf(model, protobuf, strict=strict)

    def update_from_protobuf(self, protobuf):
        value_dict = dict(map(lambda x: (x[0].name, x[1]), protobuf.ListFields()))
        for field in self._meta.fields:
            value = value_dict.get(field.attname, Null())
            if not isinstance(value, Null):
                setattr(self, field.attname, field.to_python(value))

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
