import os

from lsprotocol.types import CompletionParams, CompletionList, CompletionItem, CompletionItemKind, InsertTextFormat

import tree_utils
import utils
from parser import WOOWOO_LANGUAGE
from templatedwoowoodocument import TemplatedWooWooDocument


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

        if params.context.trigger_character == '.':
            completion_items += self.complete_include(document, params)
        elif params.context.trigger_character == ':':
            completion_items += self.complete_inner_envs(document, params)

        return completion_items


    def complete_include(self, document: TemplatedWooWooDocument, params: CompletionParams):
        """
        Check if the "include" statement would be valid and recommend files to autocomplete.
        Args:
            document:
            params:

        Returns:

        """
        # TODO: Review this condition.
        if tree_utils.is_query_overlapping_pos(document.tree, "(block) @b (object) @ob", params.position.line, max(0, params.position.character-1)):
            return []

        current_doc_path = utils.uri_to_path(params.text_document.uri)

        # relative paths of woo files in the same project as the current file
        relative_paths = [os.path.relpath(path, os.path.dirname(current_doc_path)) for path in self.ls.get_paths(document)]
        paths_joined = ",".join(relative_paths)

        return [CompletionItem(
                    label=".include",
                    kind=CompletionItemKind.Snippet,
                    insert_text_format=InsertTextFormat.Snippet,
                    insert_text=f'include ${{1|{paths_joined}|}}'
                )]


    def complete_inner_envs(self, document: TemplatedWooWooDocument, params: CompletionParams):
        """
        Autocomplete the bodies of inner environments. Behaviour entirely given by the template.
        For example, suggest possible "reference" values based on "labels" used in the document.
        .reference:<autocomplete>
        Args:
            document:
            params:

        Returns:

        """
        line, char = document.utf16_to_utf8_offset((params.position.line, params.position.character-1))

        short_inner_envs = WOOWOO_LANGUAGE.query("(short_inner_environment) @sie").captures(document.tree.root_node, start_point=(line, char), end_point=(line, char + 1))

        if len(short_inner_envs) > 0:

            short_inner_env = short_inner_envs[0][0]
            short_inner_environment_type = short_inner_env.children[1].text.decode('utf-8')

            values = set()
            for doc in self.ls.get_documents_from_project(document):
                values.update(doc.search_for_referencables_by(short_inner_environment_type))

            return [CompletionItem(label=x.decode('utf-8')) for x in values]

        else:
            return None
