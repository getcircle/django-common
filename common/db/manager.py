from django.db import models as django_models
from protobuf_to_dict import protobuf_to_dict


class CommonManager(django_models.Manager):

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def from_protobuf(self, protobuf, **extra):
        params = protobuf_to_dict(protobuf)
        params.update(extra)
        return self.create(**params)
