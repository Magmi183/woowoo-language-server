from lsprotocol.types import Diagnostic, Range, Position, DiagnosticSeverity
from parser import WOOWOO_LANGUAGE


class Linter:

    def __init__(self, ls):
        self.ls = ls

    def diagnose(self, params) -> [Diagnostic]:
        diagnostics = []
        tree = self.ls.get_document(params).tree

        # TODO: Add other types of linting.
        diagnostics += self.diagnose_errors(tree)

        # send a notification with the diagnostics to the client
        self.ls.publish_diagnostics(params.text_document.uri, diagnostics)

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
