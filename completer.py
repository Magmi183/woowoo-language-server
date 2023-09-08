import os

from lsprotocol.types import CompletionParams, CompletionList, CompletionItem, CompletionItemKind, InsertTextFormat

import tree_utils
import utils
from woowoodocument import WooWooDocument


class Completer:

    # TODO: Add trigger characters.
    trigger_characters = ['.']

    def __init__(self, ls):
        self.ls = ls

    def complete(self, params: CompletionParams) -> CompletionList:
        return CompletionList(is_incomplete=False, items=self._complete(params))

    def _complete(self, params: CompletionParams) -> [CompletionItem]:
        # https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionItem
        # TODO: Add more completion options.
        document = self.ls.get_document(params)
        completion_items = []

        completion_items += self.complete_include(document, params)

        return completion_items


    def complete_include(self, document: WooWooDocument, params: CompletionParams):

        # TODO: Do more conditions. This is POC.
        if tree_utils.is_query_overlapping_pos(document.tree, "(text_block) @tb", params.position.line, params.position.character):
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

