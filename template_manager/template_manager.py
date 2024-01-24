import yaml

from .template import Template


class TemplateManager:
    def __init__(self, template_file_path=None):
        self.active_template = None

        self.inner_environment_references = {}

        if template_file_path:
            self.load_template(template_file_path)


    def load_template(self, template_file_path):
        self.active_template = self._load_template(template_file_path)
        self.process_template()

    def _load_template(self, template_file_path):
        # TODO: Exception handling. Maybe propagate error to the user?
        with open(template_file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        return Template(**yaml_data)

    def process_template(self):
        # process short inner environments for faster lookup
        for inner in self.active_template.inner_environments:
            self.inner_environment_references[inner.name] = inner.references

        # process shorthands
        for shorthand in [self.active_template.shorthand_hash, self.active_template.shorthand_at]:
            if len(shorthand.references) > 0:
                self.inner_environment_references[shorthand.type] = shorthand.references


    def get_possible_inner_references(self, inner_environment_name):
        return self.inner_environment_references[inner_environment_name]

    def get_referencing_type_names(self):
        names = []
        for inner, references in self.inner_environment_references.items():
            if len(references) > 0:
                names.append(inner)

        return names

    def get_description(self, type: str, name: str):
        """
        Based on a tree-sitter type and its name, get description of it.
        Recognized types should be the same as the hoverable types in the LS.

        Args:
            type: tree-sitter node type (example: object_type)
            name: the name of the type (example: "Question")

        Returns: the description of the type with the given name
        """

        structure_lists = []
        if type == "outer_environment_type":
            structure_lists = [self.active_template.classic_outer_environments, self.active_template.fragile_outer_environments]
        elif type in ["short_inner_environment_type", "verbose_inner_environment_type"]:
            structure_lists = [self.active_template.inner_environments]
        elif type == "document_part_type":
            structure_lists = [self.active_template.document_parts]
        elif type == "object_type":
            structure_lists = [self.active_template.wobjects]

        for structure_list in structure_lists:
            for structure in structure_list:
                if structure.name == name:
                    return structure.description

        return None

    def get_template_name(self):
        return self.active_template.name

    def get_template_version_name(self):
        return self.active_template.version_name