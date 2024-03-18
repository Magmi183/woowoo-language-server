import logging
from typing import List, Optional

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
    FileSystemWatcher, DidChangeWatchedFilesParams, WORKSPACE_WILL_RENAME_FILES, HoverParams
from pygls.server import LanguageServer


from urllib.parse import unquote

from pygls.workspace import TextDocument
from wuff import (
    WooWooAnalyzer,
    TextDocumentIdentifier as WuffTextDocumentIdentifier,
    Position as WuffPosition,
    DefinitionParams as WuffDefinitionParams,
    RenameParams as WuffRenameParams,
    ReferenceParams as WuffReferenceParams,
)

from convertors import *
from constants import *

import logging

class WooWooLanguageServer(LanguageServer):

    def __init__(self, name: str, version: str):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Constructing WooWooLanguageServer.")
        super().__init__(name, version)
        self.analyzer = self.initialize_analyzer()

    def initialize(self, params: InitializeParams):

        if len(params.workspace_folders) != 1:
            self.logger.error("Exactly one workspace has to be opened. No other options are supported for now.")

        # default: ""
        self.set_dialect(params.initialization_options["dialectFilePath"])
        self.load_workspace(params.workspace_folders[0])

    def initialize_analyzer(self) -> WooWooAnalyzer:
        analyzer = WooWooAnalyzer()
        analyzer.set_token_types(token_types)
        analyzer.set_token_modifiers(token_modifiers)
        return analyzer

    def load_workspace(self, workspace: WorkspaceFolder):
        uri = unquote(workspace.uri)
        self.analyzer.load_workspace(uri)

    def set_dialect(self, dialect_file_path: str) -> None:
        if dialect_file_path != "":
            self.analyzer.set_dialect(dialect_file_path)
        else:
            import utils
            self.analyzer.set_dialect(utils.get_absolute_path("dialects/fit_math.yaml"))

    def diagnose(self, doc_uri: str):
        doc_uri = unquote(doc_uri)
        diagnostics = self.analyzer.diagnose(WuffTextDocumentIdentifier(doc_uri))
        lsdiagnostics = []
        for diagnostic in diagnostics:
            lsdiagnostic = wuff_diagnostic_to_ls(diagnostic)
            lsdiagnostic.source = self.name
            lsdiagnostics.append(lsdiagnostic)

        self.publish_diagnostics(doc_uri, lsdiagnostics)

    def go_to_definition(self, params: DefinitionParams) -> Optional[Location]:

        wuff_params = WuffDefinitionParams(WuffTextDocumentIdentifier(params.text_document.uri),
                                           WuffPosition(params.position.line, params.position.character))

        return wuff_location_to_ls(self.analyzer.go_to_definition(wuff_params))

    def references(self, params: ReferenceParams) -> List[Location]:

        wuff_params = WuffReferenceParams(WuffTextDocumentIdentifier(params.text_document.uri),
                                          WuffPosition(params.position.line, params.position.character),
                                          params.context.include_declaration)

        return [wuff_location_to_ls(loc) for loc in self.analyzer.references(wuff_params)]

    def rename(self, params: RenameParams) -> WorkspaceEdit:

        wuff_params = WuffRenameParams(WuffTextDocumentIdentifier(params.text_document.uri),
                                       WuffPosition(params.position.line, params.position.character),
                                       params.new_name)

        return wuff_workspace_edit_to_ls(self.analyzer.rename(wuff_params))


    def open_document(self, document_uri: str):
        self.analyzer.open_document(WuffTextDocumentIdentifier(unquote(document_uri)))

    def rename_files(self, params: RenameFilesParams) -> WorkspaceEdit:
        renames = []
        # build parameters for wuff
        for file_rename in params.files:
            renames.append((file_rename.old_uri, file_rename.new_uri))

        return wuff_workspace_edit_to_ls(self.analyzer.rename_files(renames))

    def did_delete_files(self, params: DeleteFilesParams) -> None:
        deleted_files_uris = [file_delete.uri for file_delete in params.files]
        self.analyzer.did_delete_files(deleted_files_uris)

    def document_did_change(self, document: TextDocument) -> None:
        self.analyzer.document_did_change(WuffTextDocumentIdentifier(document.uri), document.source)

    def completion(self, params: CompletionParams) -> CompletionList:
        params = completion_params_ls_to_wuff(params)
        completion_items_result = self.analyzer.complete(params)
        items = [wuff_completion_item_to_ls(item) for item in completion_items_result]
        return CompletionList(is_incomplete=False, items=items)

    def hover(self, params: TextDocumentPositionParams) -> Hover:
        doc_uri = unquote(params.text_document.uri)
        result = self.analyzer.hover(doc_uri, params.position.line, params.position.character)
        content = MarkupContent(MarkupKind.Markdown, value=result)
        return Hover(contents=content)

    def semantic_tokens(self, params: SemanticTokensParams) -> SemanticTokens:
        data = self.analyzer.semantic_tokens(unquote(params.text_document.uri))
        return SemanticTokens(data=data)

    def folding_range(self, params: FoldingRangeParams) -> List[FoldingRange]:
        folding_ranges = self.analyzer.folding_ranges(WuffTextDocumentIdentifier(unquote(params.text_document.uri)))
        return [wuff_folding_range_to_ls(item) for item in folding_ranges]