from django.db import models as django_models
from protobuf_to_dict import protobuf_to_dict
from .query import TimedQuerySet
from ...compat import metrics


class Null(object):
    pass


class CommonManager(django_models.Manager):

    def get_queryset(self):
        if metrics is not None:
            return TimedQuerySet(self.model, using=self._db, hints=self._hints)
        else:
            return super(CommonManager, self).get_queryset()

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def from_protobuf(self, protobuf, commit=True, **extra):
        values = protobuf_to_dict(protobuf)
        values.update(extra)

        model_to_protobuf_mapping = getattr(self.model, 'model_to_protobuf_mapping') or {}
        from_protobuf_transforms = getattr(self.model, 'from_protobuf_transforms') or {}
        parameters = {}
        for field in self.model._meta.fields:
            protobuf_field = model_to_protobuf_mapping.get(field.name, field.name)
            value = Null()
            if field.is_relation:
                value = values.get(protobuf_field, {}).get(field.related_field.attname, Null())

            if isinstance(value, Null):
                protobuf_field = model_to_protobuf_mapping.get(field.attname, field.attname)
                value = values.get(protobuf_field, Null())

            # only accept values for non-editable fields if they were provided
            # in extra. protects against values being passed in containers.
            if not field.editable and protobuf_field not in extra:
                continue

            if not isinstance(value, Null):
                value = field.to_python(value)
                if protobuf_field in from_protobuf_transforms:
                    value = from_protobuf_transforms[protobuf_field](value)
                parameters[field.attname] = value

        if commit:
            return self.create(**parameters)
        else:
            return self.model(**parameters)
