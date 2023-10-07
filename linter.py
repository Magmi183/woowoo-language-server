from lsprotocol.types import Diagnostic, Range, Position, DiagnosticSeverity
from parser import WOOWOO_LANGUAGE
from tree_sitter import Node


class Linter:

    def __init__(self, ls):
        self.ls = ls

    def diagnose(self, params) -> [Diagnostic]:
        diagnostics = []
        tree = self.ls.get_document(params).tree

        # TODO: Add other types of linting.
        diagnostics += self.diagnose_errors(tree)
        
        diagnostics += self.diagnose_missing_nodes(tree)

        # send a notification with the diagnostics to the client
        self.ls.publish_diagnostics(params.text_document.uri, diagnostics)

    def diagnose_missing_nodes(self, tree) -> [Diagnostic]:
        """
        Currently it is not possible to query MISSING nodes, see open issue: https://github.com/tree-sitter/tree-sitter/issues/606
        Therefore, a workaround has to be used.
        """
        diagnostics = []
        missing_nodes = []

        def traverse_tree(node: Node):
            for n in node.children:
                if n.is_missing:
                    missing_nodes.append(n)
                traverse_tree(n)

        traverse_tree(tree.root_node)
        for missing_node in missing_nodes:
            diagnostics.append(Diagnostic(
                range=Range(start=Position(*missing_node.start_point),
                            end=Position(missing_node.end_point[0], missing_node.end_point[1]+1)),
                message=f"Syntax error: MISSING {missing_node.type}",
                source=self.ls.name,
                severity=DiagnosticSeverity.Error
            ))
        
        # TODO: Add automatic fixes?

        return diagnostics

    def diagnose_errors(self, tree) -> [Diagnostic]:
        # TODO: Review and test this function.
        diagnostics = []
        query = WOOWOO_LANGUAGE.query(
            """
            (ERROR) @error
            """
        )

        error_nodes = [node for node, _ in query.captures(tree.root_node)]
        for error_node in error_nodes:
            diagnostics.append(Diagnostic(
                range=Range(start=Position(*error_node.start_point),
                            end=Position(*error_node.end_point)),
                message="Syntax error",
                source=self.ls.name,
                severity=DiagnosticSeverity.Error
            ))

        return diagnostics
