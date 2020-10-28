import jsonschema


def is_schema_valid(schema, data):
    """
    Validates whether the data is valid based on schema.
    """
    try:
        jsonschema.validate(data, schema)

    except jsonschema.ValidationError:
        return False

    else:
        return True
