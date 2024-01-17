import os

from lsprotocol.types import CompletionParams, CompletionList, CompletionItem, CompletionItemKind, InsertTextFormat

import tree_utils
import utils
from parser import WOOWOO_LANGUAGE
from woowoodocument import WooWooDocument


class Completer:

    # TODO: Add trigger characters.
    trigger_characters = ['.', ':']

    def __init__(self, ls):
        self.ls = ls

    def complete(self, params: CompletionParams) -> CompletionList:
        return CompletionList(is_incomplete=False, items=self._complete(params))

    def _complete(self, params: CompletionParams) -> [CompletionItem]:
        # https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionItem
        # TODO: Add more completion options.
        document = self.ls.get_document(params)
        completion_items = []

        # TODO: Call these methods based on trigger char., to avoid useless overhead
        completion_items += self.complete_include(document, params)
        if params.context.trigger_character == ':':
            completion_items += self.complete_inner_envs(document, params)

        return completion_items


    def complete_include(self, document: WooWooDocument, params: CompletionParams):

        # TODO: Do more conditions. This is POC.
        if tree_utils.is_query_overlapping_pos(document.tree, "(block) @b (object) @ob", params.position.line, max(0, params.position.character-1)):
            return []

        current_doc_path = utils.uri_to_path(params.text_document.uri)

        # relative paths of woo files in the workspace
        relative_paths = [os.path.relpath(path, os.path.dirname(current_doc_path)) for path in self.ls.docs.keys()]
        paths_joined = ",".join(relative_paths)

        return [CompletionItem(
                    label=".include",
                    kind=CompletionItemKind.Snippet,
                    insert_text_format=InsertTextFormat.Snippet,
                    insert_text=f'include ${{1|{paths_joined}|}}'
                )]


    def complete_inner_envs(self, document: WooWooDocument, params: CompletionParams):
        line, char = document.utf16_to_utf8_offset((params.position.line, params.position.character-1))

        short_inner_envs = WOOWOO_LANGUAGE.query("(short_inner_environment) @sie").captures(document.tree.root_node, start_point=(line, char), end_point=(line, char + 1))

        if len(short_inner_envs) > 0:

            short_inner_env = short_inner_envs[0][0]
            short_inner_environment_type = short_inner_env.children[1].text.decode('utf-8')

            possible_references = self.ls.template_manager.get_possible_short_inner_references(short_inner_environment_type)
            #TODO

            values = document.search_meta_blocks(possible_references[0])

            return [CompletionItem(label=x.decode('utf-8')) for x in values]

