import uuid


def uuid_from_hex(hex_value, version=4):
    try:
        return uuid.UUID(hex=hex_value, version=version)
    except ValueError:
        return None
