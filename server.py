import logging

from lsprotocol.types import WorkspaceFolder, DefinitionParams, ReferenceParams, RenameParams, INITIALIZE, \
    InitializeParams, \
    INITIALIZED, InitializedParams, TEXT_DOCUMENT_DID_OPEN, DidOpenTextDocumentParams, TEXT_DOCUMENT_DID_SAVE, \
    DidSaveTextDocumentParams, RenameFilesParams, WORKSPACE_DID_RENAME_FILES, \
    WORKSPACE_DID_DELETE_FILES, DeleteFilesParams, TEXT_DOCUMENT_DID_CHANGE, DidChangeTextDocumentParams, \
    TEXT_DOCUMENT_COMPLETION, CompletionOptions, CompletionList, TEXT_DOCUMENT_HOVER, TextDocumentPositionParams, \
    MarkupKind, MarkupContent, Hover, TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SemanticTokensLegend, SemanticTokensParams, \
    SemanticTokens, TEXT_DOCUMENT_DEFINITION, TEXT_DOCUMENT_REFERENCES, TEXT_DOCUMENT_RENAME, \
    TEXT_DOCUMENT_FOLDING_RANGE, FoldingRangeParams, FileOperationRegistrationOptions, FileOperationFilter, \
    FileOperationPattern, WORKSPACE_DID_CHANGE_WATCHED_FILES, DidChangeWatchedFilesRegistrationOptions, \
    FileSystemWatcher, DidChangeWatchedFilesParams, WORKSPACE_WILL_RENAME_FILES
from pygls.server import LanguageServer

from convertors import *
from constants import *
from urllib.parse import unquote

from wuff import (
    WooWooAnalyzer,
    TextDocumentIdentifier as WuffTextDocumentIdentifier,
    Position as WuffPosition,
    DefinitionParams as WuffDefinitionParams,
    RenameParams as WuffRenameParams,
    ReferenceParams as WuffReferenceParams,
)

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

    def references(self, params: ReferenceParams):

        wuff_params = WuffReferenceParams(WuffTextDocumentIdentifier(params.text_document.uri),
                                          WuffPosition(params.position.line, params.position.character),
                                          params.context.include_declaration)

        return [wuff_location_to_ls(loc) for loc in self.analyzer.references(wuff_params)]

    def rename(self, params: RenameParams):

        wuff_params = WuffRenameParams(WuffTextDocumentIdentifier(params.text_document.uri),
                                       WuffPosition(params.position.line, params.position.character),
                                       params.new_name)

        return wuff_workspace_edit_to_ls(self.analyzer.rename(wuff_params))


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


@SERVER.feature(WORKSPACE_WILL_RENAME_FILES, no_filter)
def did_rename_files(ls: WooWooLanguageServer, params: RenameFilesParams):
    logger.debug("[WORKSPACE_WILL_RENAME_FILES] notification received")

    renames = []
    # build parameters for wuff
    for file_rename in params.files:
        renames.append((file_rename.old_uri, file_rename.new_uri))

    return wuff_workspace_edit_to_ls(ls.analyzer.rename_files(renames))

@SERVER.feature(WORKSPACE_DID_DELETE_FILES, no_filter)
def did_delete_files(ls: WooWooLanguageServer, params: DeleteFilesParams):
    logger.debug("[WORKSPACE_DID_DELETE_FILES] notification received")

    deleted_files_uris = [file_delete.uri for file_delete in params.files]
    ls.analyzer.did_delete_files(deleted_files_uris)

"""
# https://github.com/openlawlibrary/pygls/issues/376

@SERVER.feature(WORKSPACE_DID_CHANGE_WATCHED_FILES, DidChangeWatchedFilesRegistrationOptions(
    watchers=[FileSystemWatcher(glob_pattern="**/*")]
))
def did_change_watched_files(ls: WooWooLanguageServer, params: DidChangeWatchedFilesParams):
    
    pass
"""


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


@SERVER.feature(TEXT_DOCUMENT_REFERENCES)
def rename(ls: WooWooLanguageServer, params: ReferenceParams):
    logger.debug("[TEXT_DOCUMENT_REFERENCES] SERVER.feature called")

    return ls.references(params)


@SERVER.feature(TEXT_DOCUMENT_RENAME)
def rename(ls: WooWooLanguageServer, params: RenameParams):
    logger.debug("[TEXT_DOCUMENT_RENAME] SERVER.feature called")

    return ls.rename(params)


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
