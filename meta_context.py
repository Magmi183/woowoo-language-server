class MetaContext:
    def __init__(self, tree, line_offset, parent_type, parent_name=None):
        self.tree = tree
        self.line_offset = line_offset
        self.parent_type = parent_type
        self.parent_name = parent_name

    def num_of_lines(self):
        return self.tree.root_node.end_point[0] - 1