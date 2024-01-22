class Reference:
    def __init__(self, structure):
        if 'meta_key' not in structure:
            raise ValueError("The 'meta_key' field is required in the structure.")

        self.meta_key = structure['meta_key'] # example: "label"
        self.structure_type = structure.get('structure_type')  # example: "outer_environment"
        self.structure_name = structure.get('structure_name')  # example: "equation"

    def __eq__(self, other):
        if not isinstance(other, Reference):
            return NotImplemented
        return (self.meta_key, self.structure_type, self.structure_name) == \
            (other.meta_key, other.structure_type, other.structure_name)

    def __hash__(self):
        return hash((self.meta_key, self.structure_type, self.structure_name))