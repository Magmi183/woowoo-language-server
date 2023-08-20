from lsprotocol.types import CompletionParams, CompletionList, CompletionItem


class Completer:

    def __init__(self, ls):
        self.ls = ls

    def complete(self, params: CompletionParams) -> CompletionList:
        return CompletionList(is_incomplete=False, items=self._complete(params))

    def _complete(self, params: CompletionParams) -> [CompletionItem]:
        # https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#completionItem
        # TODO: Do the actual work.

        return [CompletionItem(label="bold"), CompletionItem(label="italic")]
