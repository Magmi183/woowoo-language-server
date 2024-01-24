from utils import get_absolute_path
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
        'variable.other', # added
        'storage.type.struct', # added
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

        with open(get_absolute_path(file_path), 'r') as file:
            return file.read()


    # TODO: Refactor this function so that it is less redundant (less code duplication).
    def semantic_tokens(self, params: SemanticTokensParams):
        woowoo_document = self.ls.get_document(params)
        data = []

        # execute all queries from the highlights.scm file (non-metablock nodes to highlight)
        nodes = WOOWOO_LANGUAGE.query(self.woo_highlight_queries).captures(woowoo_document.tree.root_node)

        # get nodes to highlight in every meta-block of the file
        meta_blocks_nodes = self._get_meta_block_nodes(woowoo_document)

        current_meta_block_index = 0

        # line offset of the first metablock
        next_meta_block_start = (
            meta_blocks_nodes[current_meta_block_index][0]
            if current_meta_block_index < len(meta_blocks_nodes)
            else float('inf') # there are no meta-blocks in the file
        )


        cl = woowoo_document.comment_lines
        current_comment_index = 0
        next_comment = cl[0] if len(cl) > 0 else (float('inf'), 0) # (start, len)

        last_line, last_start = 0, 0
        for node in nodes:

            while node[0].start_point[0] > next_meta_block_start or node[0].start_point[0] > next_comment[0]:

                if next_meta_block_start < next_comment[0]:
                 # node is after meta-block which has NOT been processed yet, now is the time
                    processed = {}
                    for meta_block_node in meta_blocks_nodes[current_meta_block_index][1]:
                        # yaml queries allow nodes to be retrieved multiple times
                        # we skip nodes that we encounter for the second time
                        # this is possible thanks to the priority arrangment in the query file
                        if meta_block_node[0].start_point in processed: continue
                        processed[meta_block_node[0].start_point] = True

                        data, last_line, last_start = self.add_node_for_highlight(woowoo_document, data,
                                                                                       meta_block_node,
                                                                                       last_line, last_start,
                                                                                       next_meta_block_start)
                    current_meta_block_index += 1
                    next_meta_block_start = (
                        meta_blocks_nodes[current_meta_block_index][0]
                        if current_meta_block_index < len(meta_blocks_nodes)
                        else float('inf') # there are no meta-blocks in the file
                    )
                else:
                    data, last_line, last_start = self.add_comment_for_highlight(data, next_comment, last_line)
                    current_comment_index += 1
                    next_comment = cl[current_comment_index] if len(cl) > current_comment_index else (float('inf'), 0) # (start, len)


            data, last_line, last_start = self.add_node_for_highlight(woowoo_document, data, node, last_line,
                                                                           last_start)

        # All WooWoo nodes (as in highlights.scm) processed, but comments and metablock can still remain
        while current_meta_block_index < len(meta_blocks_nodes) or current_comment_index < len(cl):
            processed = {}

            # decide whether comment or meta_block is up next
            process_comment = True
            if next_meta_block_start < next_comment[0]:
                process_comment = False

            if not process_comment:
                # meta_block is next
                for meta_block_node in meta_blocks_nodes[current_meta_block_index][1]:
                    if meta_block_node[0].start_point in processed: continue
                    processed[meta_block_node[0].start_point] = True
                    data, last_line, last_start = self.add_node_for_highlight(woowoo_document, data,
                                                                                    meta_block_node,
                                                                                    last_line, last_start,
                                                                                    next_meta_block_start)

                current_meta_block_index += 1
                next_meta_block_start = float('inf')
                if current_meta_block_index < len(meta_blocks_nodes):
                    next_meta_block_start = meta_blocks_nodes[current_meta_block_index][0]
            else:
                # comment is next
                data, last_line, last_start = self.add_comment_for_highlight(data, next_comment, last_line)
                current_comment_index += 1
                next_comment = cl[current_comment_index] if len(cl) > current_comment_index else (float('inf'), 0) # (start, len)

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

    def add_comment_for_highlight(self, data, comment, last_line):
        data += [comment[0] - last_line,  # token line number, relative to the previous token
                 0,  # token start character, relative to the previous token (or start of the line)
                 comment[1],  # the length of the token.
                 Highlighter.token_types.index('comment'),  # type
                 0  # modifiers (bit encoding)
                 ]

        return data, comment[0], 0


    def adjust_bounds(self, start, end, node):

        if node.type == 'include':
            return start, (end[0], start[1] + len('.include'))
        else:
            return start, end

    def _get_meta_block_nodes(self, woowoo_document) -> [(int, [(Node, type)])]:
        # get nodes to highlight in every meta-block of the file
        meta_blocks_nodes = [] # [(metablock line offset from file start, [(Node, type)])]
        for meta_block in woowoo_document.meta_blocks:
            meta_block_nodes = YAML_LANGUAGE.query(self.yaml_highlight_queries).captures(
                meta_block.tree.root_node)
            meta_blocks_nodes.append((meta_block.line_offset, meta_block_nodes))

        return meta_blocks_nodes