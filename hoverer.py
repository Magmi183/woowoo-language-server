from lsprotocol.types import TextDocumentPositionParams, MarkupContent, MarkupKind, Hover
from parser import WOOWOO_LANGUAGE
from tree_sitter import Tree, Node
from tree_utils import build_query_string_from_list
from utils import uri_to_path


class Hoverer:
    hoverable_nodes = ["document_part_type",
                       "outer_environment_type"]

    def __init__(self, ls):
        self.ls = ls

    def hover(self, params: TextDocumentPositionParams):
        tree = self.ls.docs[uri_to_path(params.text_document.uri)].tree
        position = params.position
        line, col = position.line, position.character
        query = WOOWOO_LANGUAGE.query(build_query_string_from_list(self.hoverable_nodes, "type"))

        captures = query.captures(tree.root_node, start_point=(line, col), end_point=(line, col + 1))

        if len(captures) == 0:
            return None
        else:
            hover_text = self.get_hover_text(captures[0][0])
            content = MarkupContent(MarkupKind.Markdown, value=hover_text)
            return Hover(contents=content)

    def get_hover_text(self, node: Node):
        # TODO: Do the logic here - decide what hover text to display for this node, which we know is hoverable.
        return f"This is hoverable type, {node.type}."
