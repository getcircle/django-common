import uuid

from protobuf_to_dict import dict_to_protobuf
from protobufs.services.common import containers_pb2 as common_containers


def should_inflate_field(field_name, inflations):
    if isinstance(inflations, dict):
        inflations = dict_to_protobuf(inflations, common_containers.InflationsV1)

    should_inflate = True
    if inflations:
        if (
            not inflations.enabled or
            (inflations.exclude and field_name in inflations.exclude) or
            (inflations.only and field_name not in inflations.only) or
            inflations.disabled
        ):
            should_inflate = False
    return should_inflate


def should_populate_field(field_name, fields):
    if isinstance(fields, dict):
        fields = dict_to_protobuf(fields, common_containers.FieldsV1)

    should_populate = True
    if fields:
        if (
            (fields.only and field_name not in fields.only) or
            (fields.exclude and field_name in fields.exclude)
        ):
            should_populate = False
        return should_populate


def uuid_from_hex(hex_value, version=4):
    try:
        return uuid.UUID(hex=hex_value, version=version)
    except ValueError:
        return None


def model_choices_from_protobuf_enum(protobuf_enum):
    """Protobufs Enum "items" is the opposite order djagno requires"""
    return [(x[1], x[0]) for x in protobuf_enum.items()]
