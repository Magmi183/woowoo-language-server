import yaml

from template import Template
from document_part import DocumentPart


class TemplateManager:
    def __init__(self, yaml_location):
        self.active_template = self._load_template(yaml_location)

    def _load_template(self, yaml_location):
        with open(yaml_location, 'r') as file:
            yaml_data = yaml.safe_load(file)
        # Assuming that the top-level structure in the YAML is a Template
        return Template(**yaml_data)