from lsprotocol.types import FoldingRangeParams, FoldingRange, FoldingRangeKind

import tree_utils
from parser import WOOWOO_LANGUAGE
from woowoodocument import WooWooDocument


class Folder:

    foldable_types = ["document_part", "object", "block", "classic_outer_environment"]

    def __init__(self, ls):
        self.ls = ls

    def folding_ranges(self, params: FoldingRangeParams):
        document = self.ls.get_document(params)

        folding_ranges = []

        query = tree_utils.build_query_string_from_list(Folder.foldable_types, "any")
        nodes = WOOWOO_LANGUAGE.query(query).captures(document.tree.root_node)

        folding_ranges += self.extract_ranges_from_nodes(document, nodes)

        return folding_ranges

    def extract_ranges_from_nodes(self, document: WooWooDocument, nodes, kind="region"):
        """Simply maps tree-sitter node ranges to folding ranges, 1:1."""

        folding_ranges = []
        for node, _ in nodes:
            start_point = document.utf8_to_utf16_offset(node.start_point)
            end_point = document.utf8_to_utf16_offset(node.end_point)
            folding_range = FoldingRange(start_line=start_point[0],
                                         start_character=start_point[1],
                                         end_line=end_point[0],
                                         end_character=end_point[1],
                                         kind=FoldingRangeKind(kind))
            folding_ranges.append(folding_range)

        return folding_ranges
