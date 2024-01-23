from template_manager.meta_block import MetaBlock
from template_manager.reference import Reference


class Shorthand:
    def __init__(self, type, description, references=None, meta_block=None):
        self.type = type
        self.description = description

        self.references = [Reference(reference) for reference in references] if references else []
        self.meta_block = MetaBlock(**meta_block) if meta_block else MetaBlock()