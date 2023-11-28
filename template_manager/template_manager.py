import yaml

from template import Template


class TemplateManager:
    def __init__(self, template_file_path=None):
        self.active_template = None
        if template_file_path:
            self.load_template(template_file_path)

    def load_template(self, template_file_path):
        self.active_template = self._load_template(template_file_path)

    def _load_template(self, template_file_path):
        # TODO: Exception handling. Maybe propagate error to the user?
        with open(template_file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        return Template(**yaml_data)