from lsprotocol.types import TextDocumentPositionParams, MarkupContent, MarkupKind, Hover
from parser import WOOWOO_LANGUAGE
from tree_sitter import Tree, Node


class Hoverer:
    hoverable_nodes = ["document_part_type",
                       "outer_environment_type"]

    def __init__(self, ls):
        self.ls = ls

    def build_hoverable_nodes_query(self):
        formatted_nodes = [f"({node})" for node in self.hoverable_nodes]
        query_string = f"[ {' '.join(formatted_nodes)} ] @type"

        query = WOOWOO_LANGUAGE.query(query_string)
        return query

    def hover(self, params: TextDocumentPositionParams):
        position = params.position
        line, col = position.line, position.character
        query = self.build_hoverable_nodes_query()

        captures = query.captures(self.ls.tree.root_node, start_point=(line, col), end_point=(line, col + 1))

        if len(captures) == 0:
            return None
        else:
            hover_text = self.get_hover_text(captures[0][0])
            content = MarkupContent(MarkupKind.Markdown, value=hover_text)
            return Hover(contents=content)

    def get_hover_text(self, node: Node):
        # TODO: Do the logic here - decide what hover text to display for this node, which we know is hoverable.
        return f"This is hoverable type, {node.type}."
