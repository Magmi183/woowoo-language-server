from meta_block import MetaBlock


class InnerEnvironment:
    def __init__(self, name, description, body=None):
        self.name = name
        self.description = description
        self.body = body
