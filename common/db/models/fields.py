import json
from protobuf_to_dict import (
    protobuf_to_dict,
    dict_to_protobuf,
)

from django.core import exceptions
from django.db import models as django_models


class ProtobufField(django_models.Field):

    def __init__(self, protobuf_classes, *args, **kwargs):
        self.protobuf_classes = protobuf_classes
        super(ProtobufField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if value is None:
            return value

        content = json.loads(value)
        for protobuf_class in self.protobuf_classes:
            if protobuf_class.__name__ == content['message_class']:
                protobuf = protobuf_class()
                dict_to_protobuf(content['message_data'], protobuf)
                return protobuf
        raise exceptions.ValidationError(
            'No matching protobuf class found for: %s' % (content['message_class'],)
        )

    def get_prep_value(self, value):
        if value is None:
            return value

        if not hasattr(value, 'SerializeToString'):
            raise exceptions.ValidationError('Must be a protobuf value')

        protobuf_class = value.__class__
        if protobuf_class not in self.protobuf_classes:
            raise exceptions.ValidationError('Unregistered protobuf class: %s' % (protobuf_class,))

        content = {
            'message_class': protobuf_class.__name__,
            'message_data': protobuf_to_dict(value),
        }
        return json.dumps(content)
