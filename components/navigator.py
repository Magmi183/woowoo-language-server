from lsprotocol.types import DefinitionParams, Location, Range, Position

from parser import WOOWOO_LANGUAGE
from tree_utils import build_query_string_from_list, get_child_by_type
from utils import uri_to_path
from tree_sitter import Tree, Node


class Navigator:
    # nodes in this list MUST NOT overlap each other (one can not be child of another)
    go_to_definition_nodes = ["filename", "short_inner_environment"]

    def __init__(self, ls):
        self.ls = ls

    def go_to_definition(self, params: DefinitionParams):
        tree = self.ls.get_document(params).tree
        position = params.position
        line, col = position.line, position.character

        query = WOOWOO_LANGUAGE.query(build_query_string_from_list(self.go_to_definition_nodes, "type"))

        captures = query.captures(tree.root_node, start_point=(line, col), end_point=(line, col + 1))

        if len(captures) == 0:
            # no nodes with the capability of "go to definition" found at the position
            return None
        else:
            return self._go_to_definition(captures[-1][0], params)

    def _go_to_definition(self, node: Node, params: DefinitionParams):
        # TODO: Implement more nodes.
        if node.type == 'filename':
            filename = node.text.decode('utf-8')
            return self.get_file_location(filename, params)
        elif node.type == 'short_inner_environment':
            return self.resolve_short_inner_environment_reference(node, params)

    def get_file_location(self, filename: str, params: DefinitionParams):
        target_file_path = uri_to_path(params.text_document.uri).parent / filename
        absolute_path = target_file_path.resolve()

        file_uri = absolute_path.as_uri()
        return Location(
            uri=file_uri,
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=0)
            )
        )

    def resolve_short_inner_environment_reference(self, node: Node, params: DefinitionParams):
        short_inner_environment_type = get_child_by_type(node, "short_inner_environment_type", True)
        possible_references = self.ls.template_manager.get_possible_short_inner_references(short_inner_environment_type)

        short_inner_environment_body = get_child_by_type(node, "short_inner_environment_body", True)

        document = self.ls.get_document(params)
        project_documents = self.ls.docs[self.ls.doc_to_project[document.path]].values()

        for doc in project_documents:
            ref, line_offset = doc.find_reference(possible_references, short_inner_environment_body)
            if ref is not None:
                import urllib.parse
                import pathlib
                file_uri = urllib.parse.urljoin('file:', urllib.parse.quote(str(doc.path)))
                start_point = document.utf8_to_utf16_offset(ref.start_point)
                end_point = document.utf8_to_utf16_offset(ref.end_point)
                return Location(uri=file_uri, range=Range(
                    start=Position(line=start_point[0] + line_offset, character=start_point[1]),
                    end=Position(line=end_point[0] + line_offset, character=end_point[1])
                ))
