import logging
from pathlib import Path

from lsprotocol.types import DidChangeTextDocumentParams
from pygls.workspace import Document
from tree_sitter import Node

from parser import YAML_LANGUAGE, WOOWOO_LANGUAGE
from template_manager.reference import Reference
from typing import List, Tuple, Dict

from template_manager.template_manager import TemplateManager
from woowoodocument import WooWooDocument


class TemplatedWooWooDocument(WooWooDocument):
    """
    Template-parametrised WooWooDocument for fast and efficient template-influenced operations.
    """

    def __init__(self, path: Path, template_manager: TemplateManager):
        super().__init__(path)
        self.template_manager = template_manager

        self.referencables_values_cache = {}
        self.referencables_node_cache: Dict[Reference, Dict[str, Tuple[Node, int]]] = {}
        self.build_referencables_cache()

    def search_for_referencables_by(self, type: str):
        """Search for all referencable structures by the type given in arguments."""

        if type not in self.template_manager.get_referencing_type_names():
            # type is not able to reference anything
            return set()

        if type not in self.referencables_values_cache:
            # type is able to reference, but not in cache
            self.build_referencables_cache()

        return self.referencables_values_cache[type]



    def find_referencable(self, references: List[Reference], reference_value: str):
        """Find a structure that matches one of the references and its value is reference_value.
           Typical goto definiton.

        Args:
            references:
            reference_value:

        Returns:

        """

        for reference in references:
            if reference not in self.referencables_node_cache:
                self.build_referencables_cache()
            if reference_value in self.referencables_node_cache[reference]:
                return self.referencables_node_cache[reference][reference_value]


        return None, None


    def build_referencables_cache(self):
        """
        Caches referencable structure values and their nodes for later recovery and autocompletion.
        """

        for type in self.template_manager.get_referencing_type_names():
            references = self.template_manager.get_possible_inner_references(type)
            values = set()
            for reference in references:
                query = f"""(block_mapping_pair
                            key: (flow_node [(double_quote_scalar) (single_quote_scalar) (plain_scalar)] @key)
                            value: (flow_node) @value
                            (#eq? @key "{reference.meta_key}"))"""

                if reference not in self.referencables_node_cache:
                    self.referencables_node_cache[reference] = {}

                for meta_block in self.meta_blocks:
                    if reference.structure_type in [None, meta_block.parent_type] and reference.structure_name in [None,
                                                                                                                   meta_block.parent_name]:
                        captures = YAML_LANGUAGE.query(query).captures(meta_block.tree.root_node)
                        for node in captures:
                            if node[1] == 'value':
                                values.add(node[0].text)
                                # store the node referencable by this reference by the name
                                self.referencables_node_cache[reference][node[0].text] = node[0], meta_block.line_offset

            # store all values ('names of structs') referencable by a given type
            self.referencables_values_cache[type] = values


    def update_source_incremental(self, document: Document, params: DidChangeTextDocumentParams):
        meta_blocks_before = len(self.meta_blocks)
        super().update_source_incremental(document, params)
        meta_blocks_now = len(self.meta_blocks)

        reset_caches = False
        if meta_blocks_before != meta_blocks_now: reset_caches = True


        # check if a meta_block was changed, and if yes, clear the caches
        for change in params.content_changes:
            start_point = self.utf16_to_utf8_offset((change.range.start.line, change.range.start.character))
            end_point = self.utf16_to_utf8_offset((change.range.end.line, change.range.end.character))
            for meta_block in self.meta_blocks:
                # check if meta block range overlap with the change range
                if meta_block.line_offset <= end_point[0] and start_point[0] <= meta_block.line_offset + meta_block.num_of_lines():
                    reset_caches = True
                    break

        if reset_caches:
            self.referencables_values_cache = {}
            self.referencables_node_cache = {}