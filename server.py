import logging

from pygls.server import LanguageServer

from convertors import *
from constants import *
from urllib.parse import unquote

from wuff import (
    WooWooAnalyzer,
    TextDocumentIdentifier as WuffTextDocumentIdentifier,
    Position as WuffPosition,
    DefinitionParams as WuffDefinitionParams,
)



# TODO: Setup logging better.
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WooWooLanguageServer(LanguageServer):

    def __init__(self, name: str, version: str):
        logger.debug("Constructing WooWooLanguageServer.")
        super().__init__(name, version)
        self.analyzer = self.initialize_analyzer()

    def initialize_analyzer(self):
        analyzer = WooWooAnalyzer()
        analyzer.set_token_types(token_types)
        analyzer.set_token_modifiers(token_modifiers)
        return analyzer

    def load_workspace(self, workspace: WorkspaceFolder):
        uri = unquote(workspace.uri)
        self.analyzer.load_workspace(uri)


    def set_dialect(self, dialect_file_path):
        # TODO: better fallback mechanisms and error handling + handle default template better
        if dialect_file_path != "":
            self.analyzer.set_dialect(dialect_file_path)
        else:
            import utils
            self.analyzer.set_dialect(utils.get_absolute_path("dialects/fit_math.yaml"))

    def diagnose(self, doc_uri):
        doc_uri = unquote(doc_uri)
        diagnostics = self.analyzer.diagnose(WuffTextDocumentIdentifier(doc_uri))
        lsdiagnostics = []
        for diagnostic in diagnostics:
            lsdiagnostic = wuff_diagnostic_to_ls(diagnostic)
            lsdiagnostic.source = self.name
            lsdiagnostics.append(lsdiagnostic)

        self.publish_diagnostics(doc_uri, lsdiagnostics)

    def go_to_definition(self, params: DefinitionParams):

        wuff_params = WuffDefinitionParams(WuffTextDocumentIdentifier(params.text_document.uri),
                                           WuffPosition(params.position.line, params.position.character))

        return wuff_location_to_ls(self.analyzer.go_to_definition(wuff_params))




SERVER = WooWooLanguageServer('woowoo-language-SERVER', 'v0.1')


@SERVER.feature(INITIALIZE)
def initiliaze(ls: WooWooLanguageServer, params: InitializeParams) -> None:
    logger.debug("[INITIALIZE]")

    if len(params.workspace_folders) != 1:
        logger.error("Exactly one workspace has to be opened. No other options are supported for now.")

    # default: ""
    ls.set_dialect(params.initialization_options["dialectFilePath"])

    ls.load_workspace(params.workspace_folders[0])


@SERVER.feature(INITIALIZED)
def initiliazed(_ls: WooWooLanguageServer, params: InitializedParams) -> None:
    logger.debug("[INITIALIZED] Connection was established.")

@SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: WooWooLanguageServer, params: DidOpenTextDocumentParams):
    logger.debug("[TEXT_DOCUMENT_DID_OPEN] SERVER.feature called")

    ls.analyzer.open_document(WuffTextDocumentIdentifier(unquote(params.text_document.uri)))
    ls.diagnose(unquote(params.text_document.uri))


@SERVER.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: WooWooLanguageServer, params: DidSaveTextDocumentParams) -> None:
    logger.debug("[TEXT_DOCUMENT_DID_SAVE] SERVER.feature called")

    ls.diagnose(unquote(params.text_document.uri))


@SERVER.feature(WORKSPACE_WILL_RENAME_FILES)
def will_rename_files(ls: WooWooLanguageServer, params: RenameFilesParams):
    logger.debug("[WORKSPACE_WILL_RENAME_FILES] SERVER.feature called")

    # TODO: Refactor file references to the new name (like in .include statements)
    # https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#renameFilesParams


@SERVER.feature(WORKSPACE_DID_RENAME_FILES)
def did_rename_files(ls: WooWooLanguageServer, params: RenameFilesParams):
    logger.debug("[WORKSPACE_DID_RENAME_FILES] notification received")
    # TODO: Test  (analyzer).
    for file_rename in params.files:
        old_uri, new_uri = file_rename.old_uri, file_rename.new_uri
        ls.analyzer.rename_document(old_uri, new_uri)


# TODO: Handle file deletion!

@SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: WooWooLanguageServer, params: DidChangeTextDocumentParams):
    logger.debug("[TEXT_DOCUMENT_DID_CHANGE] SERVER.feature called")
    # do not unquote before this function call!
    doc = ls.workspace.get_document(params.text_document.uri)
    doc_uri = unquote(params.text_document.uri)
    ls.analyzer.document_did_change(WuffTextDocumentIdentifier(doc_uri), doc.source)
    ls.diagnose(doc_uri)


@SERVER.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=trigger_characters))
def completions(ls: WooWooLanguageServer, params: CompletionParams):
    logger.debug("[TEXT_DOCUMENT_COMPLETION] SERVER.feature called")
    params = completion_params_ls_to_wuff(params)
    completion_items_result = ls.analyzer.complete(params)
    items = [wuff_completion_item_to_ls(item) for item in completion_items_result]
    return CompletionList(is_incomplete=False, items=items)


@SERVER.feature(TEXT_DOCUMENT_HOVER)
def on_hover(ls: WooWooLanguageServer, params: TextDocumentPositionParams):
    logger.debug("[TEXT_DOCUMENT_HOVER] SERVER.feature called")
    doc_uri = unquote(params.text_document.uri)
    result = ls.analyzer.hover(doc_uri, params.position.line, params.position.character)
    content = MarkupContent(MarkupKind.Markdown, value=result)
    return Hover(contents=content)


@SERVER.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                SemanticTokensLegend(token_types=token_types,
                                     token_modifiers=token_modifiers))
def semantic_tokens(ls: WooWooLanguageServer, params: SemanticTokensParams):
    logger.debug("[TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL] SERVER.feature called")
    data = ls.analyzer.semantic_tokens(unquote(params.text_document.uri))
    return SemanticTokens(data=data)


@SERVER.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: WooWooLanguageServer, params: DefinitionParams):
    logger.debug("[TEXT_DOCUMENT_DEFINITION] SERVER.feature called")

    return ls.go_to_definition(params)


@SERVER.feature(TEXT_DOCUMENT_FOLDING_RANGE)
def folding_range(ls: WooWooLanguageServer, params: FoldingRangeParams):
    logger.debug("[TEXT_DOCUMENT_FOLDING_RANGE] SERVER.feature called")

    folding_ranges = ls.analyzer.folding_ranges(WuffTextDocumentIdentifier(unquote(params.text_document.uri)))
    data = [wuff_folding_range_to_ls(item) for item in folding_ranges]
    return data


def start() -> None:
    SERVER.start_io()


if __name__ == "__main__":
    start()
