from lsprotocol.types import SemanticTokens, SemanticTokensParams
from tree_sitter import Node

from parser import WOOWOO_LANGUAGE, YAML_LANGUAGE


class Highlighter:
    # the token types recognized by VSCode client
    token_types = [
        'namespace',
        'type',
        'class',
        'enum',
        'interface',
        'struct',
        'typeParameter',
        'parameter',
        'variable',
        'property',
        'enumMember',
        'event',
        'function',
        'method',
        'macro',
        'keyword',
        'modifier',
        'comment',
        'string',
        'number',
        'regexp',
        'operator',
        'decorator',
    ]
    token_modifiers = [
        'declaration',
        'definition',
        'readonly',
        'static',
        'deprecated',
        'abstract',
        'async',
        'modification',
        'documentation',
        'defaultLibrary'
    ]

    def __init__(self, ls):
        self.ls = ls
        self.woo_highlight_queries = self.read_highlights('queries/highlights.scm')
        self.yaml_highlight_queries = self.read_highlights('queries/yaml-highlights.scm')

    def read_highlights(self, file_path) -> str:

        with open(file_path, 'r') as file:
            return file.read()

    def semantic_tokens(self, params: SemanticTokensParams):
        woowoo_document = self.ls.get_document(params)
        data = []

        # execute all queries from the highlights.scm file (non-metablock nodes to highlight)
        nodes = WOOWOO_LANGUAGE.query(self.woo_highlight_queries).captures(woowoo_document.tree.root_node)

        # get nodes to highlight in every meta-block of the file
        meta_blocks_nodes = [] # [(metablock line offset from file start, [(Node, type)])]
        for line_offset, meta_block_tree in woowoo_document.meta_block_trees:
            meta_block_nodes = YAML_LANGUAGE.query(self.yaml_highlight_queries).captures(
                meta_block_tree.root_node)
            meta_blocks_nodes.append((line_offset, meta_block_nodes))


        current_meta_block_index = 0
        next_meta_block_start = float('inf') # line offset of the first metablock
        if current_meta_block_index < len(meta_blocks_nodes):
            next_meta_block_start = meta_blocks_nodes[current_meta_block_index][0]

        last_line, last_start = 0, 0
        for node in nodes:

            while node[0].start_point[0] > next_meta_block_start:
                # node is after meta-block which has NOT been processed yet, now is the time
                for meta_block_node in meta_blocks_nodes[current_meta_block_index][1]:
                    data, last_line, last_start = self.add_node_for_highlight(woowoo_document, data,
                                                                                   meta_block_node,
                                                                                   last_line, last_start,
                                                                                   next_meta_block_start)

                current_meta_block_index += 1
                next_meta_block_start = float('inf')
                if current_meta_block_index < len(meta_blocks_nodes):
                    next_meta_block_start = meta_blocks_nodes[current_meta_block_index][0]

            data, last_line, last_start = self.add_node_for_highlight(woowoo_document, data, node, last_line,
                                                                           last_start)

        # all non-meta block processed, but meta-block could still remain (if they are last nodes of the file)
        while current_meta_block_index < len(meta_blocks_nodes):
            for meta_block_node in meta_blocks_nodes[current_meta_block_index][1]:
                data, last_line, last_start = self.add_node_for_highlight(woowoo_document, data,
                                                                                meta_block_node,
                                                                                last_line, last_start,
                                                                                next_meta_block_start)

            current_meta_block_index += 1
            next_meta_block_start = float('inf')
            if current_meta_block_index < len(meta_blocks_nodes):
                next_meta_block_start = meta_blocks_nodes[current_meta_block_index][0]

        return SemanticTokens(data=data)

    def add_node_for_highlight(self, woowoo_document, data, node, last_line, last_start, line_offset=0):
        # TODO: Inspect why YAML parser does sometimes return just Nodes, not tuples
        if isinstance(node, Node): return data, node, last_line, last_start

        node, type = node

        # restart char position index when current token is on different line than the previous one
        last_start = last_start if node.start_point[0] + line_offset == last_line else 0

        start_point = woowoo_document.utf8_to_utf16_offset((node.start_point[0] + line_offset, node.start_point[1]))
        end_point = woowoo_document.utf8_to_utf16_offset((node.end_point[0] + line_offset, node.end_point[1]))

        # this adjustment is needed because vscode does not support overlapping tokens ('include' token in this case)
        # the tree-sitter grammar would have to be changed (named node would have to be introduced) to get rid of this
        start_point, end_point = self.adjust_bounds(start_point, end_point, node)

        data += [start_point[0] - last_line,  # token line number, relative to the previous token
                 start_point[1] - last_start,  # token start character, relative to the previous token (or start of the line)
                 end_point[1] - start_point[1],  # the length of the token.
                 Highlighter.token_types.index(type),  # type
                 0  # modifiers (bit encoding)
                 ]

        last_line, last_start = start_point

        return data, last_line, last_start

    def adjust_bounds(self, start, end, node):

        if node.type == 'include':
            return start, (end[0], start[1] + len('.include'))
        else:
            return start, end
