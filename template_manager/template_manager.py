import yaml

from .template import Template


class TemplateManager:
    def __init__(self, template_file_path=None):
        self.active_template = None

        self.short_inner_environment_references = {}

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
        for short_inner in self.active_template.short_inner_environemnts:
            self.short_inner_environment_references[short_inner.name] = short_inner.references


    def get_possible_short_inner_references(self, short_inner_environment_name):
        return self.short_inner_environment_references[short_inner_environment_name]

    def get_referencing_type_names(self):
        names = []
        for short_inner, references in self.short_inner_environment_references.items():
            if len(references) > 0:
                names.append(short_inner)

        return names