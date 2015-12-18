import uuid
from django.db.models import *  # NOQA
from django.db import models as django_models
from django.db.models import options
from protobuf_to_dict import (
    dict_to_protobuf,
    protobuf_to_dict,
)

from .manager import CommonManager
from ...utils import should_populate_field

# Support specifying protobuf in model meta
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('protobuf',)


class Null(object):
    pass


class Model(django_models.Model):

    from_protobuf_transforms = None
    model_to_protobuf_mapping = None
    as_dict_value_transforms = None
    objects = CommonManager()

    def as_dict(self, extra=tuple(), fields=None):
        if self.as_dict_value_transforms is None:
            self.as_dict_value_transforms = {}

        output = {}
        for field in self._meta.fields:
            if not should_populate_field(field.attname, fields):
                continue

            value = field.value_from_object(self)
            transform = self.as_dict_value_transforms.get(field.name)
            if transform is not None and callable(transform):
                value = transform(value)
            elif hasattr(field, 'as_dict_value_transform'):
                value = field.as_dict_value_transform(value)
            elif not isinstance(value, (bool, None.__class__, dict)):
                value = field.value_to_string(self)
            output[field.attname] = value

        for attribute in extra:
            if not should_populate_field(attribute, fields):
                continue

            value = getattr(self, attribute, None)
            output[attribute] = value

        return output

    @classmethod
    def verify_has_protobuf(cls):
        if cls._meta.protobuf is None:
            raise NotImplementedError('Must define `protobuf` in meta')

    def new_protobuf_container(self, protobuf=None, **kwargs):
        if protobuf is None:
            self.verify_has_protobuf()
            protobuf = self._meta.protobuf()
        return protobuf

    def to_protobuf(
            self,
            protobuf=None,
            strict=False,
            extra=None,
            fields=None,
            inflations=None,
            **overrides
        ):
        protobuf = self.new_protobuf_container(protobuf)

        if extra is None:
            extra = []

        if self.model_to_protobuf_mapping is None:
            self.model_to_protobuf_mapping = {}

        model = self.as_dict(extra=extra, fields=fields)
        model.update(overrides)
        for model_field, protobuf_field in self.model_to_protobuf_mapping.iteritems():
            model[protobuf_field] = model.pop(model_field, None)

        for field in getattr(self, 'protobuf_exclude_fields', []):
            model.pop(field, None)

        return dict_to_protobuf(model, protobuf, strict=strict)

    def update_from_protobuf(self, protobuf, **overrides):
        if self.model_to_protobuf_mapping is None:
            self.model_to_protobuf_mapping = {}

        # XXX we shouldn't allow updating changed and created, look into editable=False
        value_dict = dict(map(lambda x: (x[0].name, x[1]), protobuf.ListFields()))
        for field in self._meta.fields:
            if not field.editable:
                continue

            protobuf_field = self.model_to_protobuf_mapping.get(field.attname, field.attname)
            if protobuf_field in overrides:
                value = overrides[protobuf_field]
            else:
                value = value_dict.get(protobuf_field, Null())

            if hasattr(value, 'FromString'):
                value = protobuf_to_dict(value)

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


class SafelyDeletableModel(Model):

    DELETED_STATUS = 1
    STATUS_CHOICES = (
        (DELETED_STATUS, 'Deleted'),
    )

    status = django_models.PositiveSmallIntegerField(null=True, choices=STATUS_CHOICES)

    class Meta:
        abstract = True
