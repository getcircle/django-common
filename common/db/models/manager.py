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

        model_to_protobuf_mapping = getattr(self.model, 'model_to_protobuf_mapping', {})
        parameters = {}
        for field in self.model._meta.fields:
            protobuf_field = model_to_protobuf_mapping.get(field.name, field.name)
            value = Null()
            if field.is_relation:
                value = values.get(protobuf_field, {}).get(field.related_field.attname, Null())

            if isinstance(value, Null):
                value = values.get(protobuf_field, Null())

            if not isinstance(value, Null):
                parameters[field.attname] = field.to_python(value)

        if commit:
            return self.create(**parameters)
        else:
            return self.model(**parameters)
