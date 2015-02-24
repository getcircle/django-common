import uuid
from django.db.models import *  # NOQA
from django.db import models as django_models
from protobuf_to_dict import dict_to_protobuf

from .manager import CommonManager


class Null(object):
    pass


class Model(django_models.Model):

    as_dict_value_transforms = None
    objects = CommonManager()

    def as_dict(self, extra=tuple(), exclude=tuple()):
        if self.as_dict_value_transforms is None:
            self.as_dict_value_transforms = {}

        output = {}
        for field in self._meta.fields:
            value = field.value_from_object(self)
            if not isinstance(value, (bool, None.__class__)):
                transform = self.as_dict_value_transforms.get(field.name)
                if transform is not None and callable(transform):
                    value = transform(value)
                else:
                    value = field.value_to_string(self)
            output[field.attname] = value

        for attribute in extra:
            value = getattr(self, attribute, None)
            output[attribute] = value

        for field in exclude:
            output.pop(field, None)

        return output

    def to_protobuf(self, protobuf, strict=False, extra=None, **overrides):
        if extra is None:
            extra = []

        extra.extend(getattr(self, 'protobuf_include_fields', []))
        model = self.as_dict(extra=extra)
        model.update(overrides)
        for field in getattr(self, 'protobuf_exclude_fields', []):
            model.pop(field, None)
        return dict_to_protobuf(model, protobuf, strict=strict)

    def update_from_protobuf(self, protobuf, **overrides):
        # XXX we shouldn't allow updating changed and created, look into editable=False
        value_dict = dict(map(lambda x: (x[0].name, x[1]), protobuf.ListFields()))
        for field in self._meta.fields:
            if field.attname in overrides:
                value = overrides[field.attname]
            else:
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
