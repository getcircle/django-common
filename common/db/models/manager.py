from django.db import models as django_models
from protobuf_to_dict import protobuf_to_dict
from ..compat import metrics
from .query import TimedQuerySet


class Null(object):
    pass


class CommonManager(django_models.Manager):

    def get_queryset(self):
        if metris is not None:
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

        parameters = {}
        for field in self.model._meta.fields:
            value = Null()
            if field.is_relation:
                value = values.get(field.name, {}).get(field.related_field.attname, Null())

            if isinstance(value, Null):
                value = values.get(field.attname, Null())

            if not isinstance(value, Null):
                parameters[field.attname] = field.to_python(value)

        if commit:
            return self.create(**parameters)
        else:
            return self.model(**parameters)
