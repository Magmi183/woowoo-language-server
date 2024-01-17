from .meta_block import MetaBlock
from .reference import Reference


class InnerEnvironment:
    def __init__(self, name, description, references=None):
        self.name = name
        self.description = description
        if references:
            self.references = [Reference(reference) for reference in references]
        else:
            self.references = None
