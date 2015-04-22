import uuid


def uuid_from_hex(hex_value, version=4):
    try:
        return uuid.UUID(hex=hex_value, version=version)
    except ValueError:
        return None


def model_choices_from_protobuf_enum(protobuf_enum):
    """Protobufs Enum "items" is the opposite order djagno requires"""
    return [(x[1], x[0]) for x in protobuf_enum.items()]
