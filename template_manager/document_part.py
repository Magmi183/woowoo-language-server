from .meta_block import MetaBlock


class DocumentPart:
    def __init__(self, name, description, meta_block=None):
        self.name = name
        self.description = description
        self.meta_block = MetaBlock(**meta_block) if meta_block else MetaBlock()
