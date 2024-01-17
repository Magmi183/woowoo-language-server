from .template_manager import TemplateManager
from pprint import pprint

# Test script

yaml_path = '/Users/michaljanecek/Diplomka/woowoo-pygls/template_sandbox/fit_math.yaml'

template_manager = TemplateManager(yaml_path)

template = template_manager.active_template

