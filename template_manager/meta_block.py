from .field import Field


class MetaBlock:
    def __init__(self, required_fields=None, optional_fields=None):
        # If fields are provided, create Field instances, otherwise use empty lists
        self.required_fields = [Field(**rf) for rf in (required_fields or [])]
        self.optional_fields = [Field(**of) for of in (optional_fields or [])]
