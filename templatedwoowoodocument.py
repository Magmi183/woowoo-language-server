import logging
from pathlib import Path

from lsprotocol.types import DidChangeTextDocumentParams
from pygls.workspace import Document

from meta_context import MetaContext
from parser import parse_source, YAML_LANGUAGE, woowoo_parser, parse_metas, WOOWOO_LANGUAGE
from template_manager.reference import Reference
from typing import List

from template_manager.template_manager import TemplateManager
from woowoodocument import WooWooDocument


class TemplatedWooWooDocument(WooWooDocument):
    """
    Template-parametrised WooWooDocument for fast and efficient template-influenced operations.
    """

    def __init__(self, path: Path, template_manager: TemplateManager):
        super().__init__(path)
        self.template_manager = template_manager

        self.referencables_cache = {}
        self.build_referencables_cache()

    def search_for_referencables_by(self, type: str):
        """Search for all k:v pairs in meta blocks that follow the structure in reference.
         Collect all values and return them."""

        if type in self.referencables_cache:
            return self.referencables_cache[type]

        references = self.template_manager.get_possible_short_inner_references(type)
        nodes_all = []
        for reference in references:
            query = f"""(block_mapping_pair
                key: (flow_node [(double_quote_scalar) (single_quote_scalar) (plain_scalar)] @key)
                value: (flow_node) @value
                (#eq? @key "{reference.meta_key}"))"""

            for meta_block in self.meta_blocks:
                if reference.structure_type in [None, meta_block.parent_type] and reference.structure_name in [None, meta_block.parent_name]:
                    nodes_all += YAML_LANGUAGE.query(query).captures(meta_block.tree.root_node)

        values = set()
        for node in nodes_all:
            if node[1] == 'value':
                values.add(node[0].text)

        self.referencables_cache[type] = values
        return values


    def find_reference(self, references: List[Reference], reference_value: str):

        for reference in references:
            query = f"""(block_mapping_pair
                        key: (flow_node [(double_quote_scalar) (single_quote_scalar) (plain_scalar)] @key)
                        value: (flow_node) @value
                        (#eq? @key "{reference.meta_key}")
                        (#eq? @value "{reference_value}"))"""

            for meta_block in self.meta_blocks:
                if reference.structure_type in [None, meta_block.parent_type] and reference.structure_name in [None,
                                                                                                               meta_block.parent_name]:
                    captures = YAML_LANGUAGE.query(query).captures(meta_block.tree.root_node)
                    if len(captures) > 0:
                        for capture in captures:
                            if capture[1] == 'value':
                                return capture[0], meta_block.line_offset

        return None, None


    def build_referencables_cache(self):

        for referencing_type in self.template_manager.get_referencing_type_names():
            self.search_for_referencables_by(referencing_type)


    def update_source_incremental(self, document: Document, params: DidChangeTextDocumentParams):
        super().update_source_incremental(document, params)

        for change in params.content_changes:
            start_point = self.utf16_to_utf8_offset((change.range.start.line, change.range.start.character))
            end_point = self.utf16_to_utf8_offset((change.range.end.line, change.range.end.character))
            metas = (WOOWOO_LANGUAGE.query("(meta_block) @mb")
                     .captures(self.tree.root_node, start_point=start_point, end_point=end_point))
            if len(metas) > 0:
                self.referencables_cache = {}
                break