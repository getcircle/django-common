import uuid

from protobuf_to_dict import dict_to_protobuf
from protobufs.services.common import containers_pb2 as common_containers

REPEATED_ITEM_FORMAT = '[]%s'


def strip_field_name(field_name, original_array):
    new_array = []
    field_name = field_name + '.'
    for value in original_array:
        if value.startswith(field_name):
            try:
                stripped = value.split(field_name, 1)[1]
            except IndexError:
                continue
            else:
                if stripped:
                    new_array.append(stripped)
    return new_array


def fields_for_repeated_item(field_name, fields):
    """Unpack field specifications for repeated items.

    Given the following message:

        message Item {
            string title = 1;
        }

        message Something {
            repeated Item items = 1;
        }

    We support specifying sepcific fields that should be returned for the
    repeated containers given a format of:

        {'only': ['[]items.title']}

    This should unpack for each item as:

        {'only': ['title']}

    """
    repeated_item_key = REPEATED_ITEM_FORMAT % (field_name,)
    return fields_for_item(repeated_item_key, fields)


def fields_for_item(field_name, fields):
    """Unpack field specifications for the specific item.

    Given the following message:

        message Item {
            string title = 1;
        }

        message Something {
            message Item item = 1;
        }

    We support specifying fields that should be returned for nested items given a format of:

        {'only': ['item.title']}

    This should unpack for the item as:

        {'only': ['title']}

    """
    if isinstance(fields, dict):
        fields = dict_to_protobuf(fields, common_containers.FieldsV1)

    fields_for_item = common_containers.FieldsV1()
    fields_for_item.only.extend(strip_field_name(field_name, fields.only))
    fields_for_item.exclude.extend(strip_field_name(field_name, fields.exclude))
    return fields_for_item


def inflations_for_repeated_item(field_name, inflations):
    """Unpack inflation specifications for repeated items.

    Given the following message:

        message Item {
            string title = 1;
        }

        message Something {
            repeated Item items = 1;
        }

    We support specifying sepcific inflations that should be returned for the
    repeated containers given a format of:

        {'only': ['[]items.title']}

    This should unpack for each item as:

        {'only': ['title']}

    """
    repeated_item_key = REPEATED_ITEM_FORMAT % (field_name,)
    return inflations_for_item(repeated_item_key, inflations)


def inflations_for_item(field_name, inflations):
    """Unpack inflation specifications for the specific item.

    Given the following message:

        message Item {
            string title = 1;
        }

        message Something {
            message Item item = 1;
        }

    We support specifying inflations that should be returned for nested items
    given a format of:

        {'only': ['item.title']}

    This should unpack for the item as:

        {'only': ['title']}

    """
    if isinstance(inflations, dict):
        inflations = dict_to_protobuf(inflations, common_containers.InflationsV1)

    inflations_for_item = common_containers.InflationsV1()
    if inflations.disabled:
        inflations_for_item.disabled = True
        return inflations_for_item

    inflations_for_item.only.extend(strip_field_name(field_name, inflations.only))
    inflations_for_item.exclude.extend(strip_field_name(field_name, inflations.exclude))
    return inflations_for_item


def should_inflate_field(field_name, inflations):
    if isinstance(inflations, dict):
        inflations = dict_to_protobuf(inflations, common_containers.InflationsV1)

    should_inflate = True
    if inflations:
        if (
            inflations.disabled or
            (inflations.exclude and field_name in inflations.exclude) or
            (inflations.only and field_name not in inflations.only)
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
