class Reference:
    def __init__(self, structure):
        if 'meta_key' not in structure:
            raise ValueError("The 'meta_key' field is required in the structure.")

        self.meta_key = structure['meta_key'] # example: "label"
        self.structure_type = structure.get('structure_type')  # example: "outer_environment"
        self.structure_name = structure.get('structure_name')  # example: "equation"

