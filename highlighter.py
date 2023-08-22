import re

from lsprotocol.types import SemanticTokens

from parser import WOOWOO_LANGUAGE

class Highlighter:
    # the token types/modifiers used by the highlighter
    token_types = [
        "comment",
        "string",
        "string.delimiter",
        "keyword",
        "number",
        "regexp",
        "operator",
        "namespace",
        "type",
        "struct",
        "class",
        "interface",
        "enum",
        "typeParameter",
        "function",
        "member",
        "macro",
        "variable",
        "parameter",
        "label",
        "property",
        "enumMember",
        "event",
        "operator.overloaded",
        "constant"
    ]
    token_modifiers = []

    def __init__(self, ls):
        self.ls = ls
        self.highlight_queries = self.read_highlights()

    def read_highlights(self) -> str:
        """
        Reads the contents of the 'queries/highlights.scm' file. This is the same file used by tree-sitter.
        It can be used to make one big capture-all query.

        :return: A string containing the contents of the 'queries/highlights.scm' file.
        """
        with open('queries/highlights.scm', 'r') as file:
            return file.read()

    def semantic_tokens(self):
        data = []

        # execute all queries from the highlights.scm file
        nodes = WOOWOO_LANGUAGE.query(self.highlight_queries).captures(self.ls.tree.root_node)

        last_line, last_start = 0, 0
        for node in nodes:
            node, type = node

            # restart char position index when current token is on different line than the previous one
            last_start = last_start if node.start_point[0] == last_line else 0

            data += [node.start_point[0] - last_line,  # token line number, relative to the previous token
                     node.start_point[1] - last_start,  # token start character, relative to the previous token
                     node.end_point[1] - node.start_point[1],  # the length of the token.
                     Highlighter.token_types.index(type),  # type
                     0  # modifiers (bit encoding)
                     ]

            last_line, last_start = node.start_point

        return SemanticTokens(data=data)
