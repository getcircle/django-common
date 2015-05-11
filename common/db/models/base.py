import uuid
from django.db.models import *  # NOQA
from django.db import models as django_models
from django.db.models import options
from protobuf_to_dict import dict_to_protobuf

from .manager import CommonManager

# Support specifying protobuf in model meta
options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('protobuf',)


class Null(object):
    pass


class Model(django_models.Model):

    model_to_protobuf_mapping = None
    as_dict_value_transforms = None
    objects = CommonManager()

    def as_dict(self, extra=tuple(), exclude=tuple(), only=tuple()):
        if self.as_dict_value_transforms is None:
            self.as_dict_value_transforms = {}

        output = {}
        for field in self._meta.fields:
            if only and field.attname not in only:
                continue
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

    @classmethod
    def verify_has_protobuf(cls):
        if cls._meta.protobuf is None:
            raise NotImplementedError('Must define `protobuf` in meta')

    def to_protobuf(self, protobuf=None, strict=False, extra=None, only=tuple(), **overrides):
        if protobuf is None:
            self.verify_has_protobuf()
            protobuf = self._meta.protobuf()

        if extra is None:
            extra = []

        if not only:
            extra.extend(getattr(self, 'protobuf_include_fields', []))

        if self.model_to_protobuf_mapping is None:
            self.model_to_protobuf_mapping = {}

        model = self.as_dict(extra=extra, only=only)
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
            protobuf_field = self.model_to_protobuf_mapping.get(field.attname, field.attname)
            if protobuf_field in overrides:
                value = overrides[protobuf_field]
            else:
                value = value_dict.get(protobuf_field, Null())
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
