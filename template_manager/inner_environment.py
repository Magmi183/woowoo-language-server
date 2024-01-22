from .meta_block import MetaBlock
from .reference import Reference


class InnerEnvironment:
    def __init__(self, name, description, references=None, meta_block=None):
        self.name = name
        self.description = description

        self.references = [Reference(reference) for reference in references] if references else []
        self.meta_block = MetaBlock(**meta_block) if meta_block else MetaBlock()