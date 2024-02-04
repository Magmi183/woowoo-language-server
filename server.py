import logging
from pathlib import Path

from pygls.server import LanguageServer

import utils
from components.completer import Completer
from components.navigator import Navigator

from template_manager.template_manager import TemplateManager
from constants import *

from Wuff import (
    WooWooAnalyzer,
    CompletionParams as WuffCompletionParams,
    TextDocumentIdentifier as WuffTextDocumentIdentifier,
    Position as WuffPosition,
    CompletionContext as WuffCompletionContext,
    CompletionTriggerKind as WuffCompletionTriggerKind,
    CompletionItem as WuffCompletionItem,
    InsertTextFormat as WuffInsertTextFormat,
    CompletionItemKind as WuffCompletionItemKind,
    Diagnostic as WuffDiagnostic,
    DiagnosticSeverity as WuffDiagnosticSeverity
)

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionParams as LSCompletionParams, DidOpenTextDocumentParams, DidChangeTextDocumentParams,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    CompletionOptions, INITIALIZED, TEXT_DOCUMENT_DEFINITION, TEXT_DOCUMENT_DID_SAVE,
    DidSaveTextDocumentParams, TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SemanticTokensParams,
    SemanticTokensLegend, InitializedParams, InitializeParams, INITIALIZE,
    WorkspaceFolder, DefinitionParams, TEXT_DOCUMENT_FOLDING_RANGE, FoldingRangeParams, WORKSPACE_DID_RENAME_FILES,
    RenameFilesParams, WORKSPACE_WILL_RENAME_FILES, TEXT_DOCUMENT_HOVER, TextDocumentPositionParams, MarkupContent,
    MarkupKind, Hover, SemanticTokens, CompletionList
)

from convertors import *

from templatedwoowoodocument import TemplatedWooWooDocument

# TODO: Setup logging better.
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WooWooLanguageServer(LanguageServer):

    def __init__(self, name: str, version: str):
        logger.debug("Constructing WooWooLanguageServer.")
        super().__init__(name, version)

        self.template_manager = TemplateManager()

        self.completer = Completer(self)
        self.navigator = Navigator(self)

        self.docs = {}
        self.doc_to_project = {}

        self.analyzer = self.initialize_analyzer()

    def initialize_analyzer(self):
        analyzer = WooWooAnalyzer()
        analyzer.set_token_types(token_types)
        analyzer.set_token_modifiers(token_modifiers)
        return analyzer

    def load_workspace(self, workspace: WorkspaceFolder):

        self.analyzer.load_workspace(workspace.uri)
        root_path = utils.uri_to_path(workspace.uri)
        project_folders = self.find_project_folders(root_path)
        

        for project_folder in project_folders:
            woo_files = project_folder.rglob('*.woo')
            for woo_file in woo_files:
                self.load_document(woo_file, project_folder)

        # other .woo files, not in any project
        for woo_file in root_path.glob('*.woo'):
            if woo_file not in self.doc_to_project:
                self.load_document(woo_file, None)


        

    def find_project_folders(self, root_path: Path):
        # Find all folders containing a Woofile
        return [path.parent for path in root_path.rglob('Woofile')]

    def find_project_folder(self, path: Path):
        # Find project folder for a given file.

        for parent in path.parents:
            # Check if this directory has a 'Woofile'
            if (parent / 'Woofile').exists():
                return parent
        return None

    def load_document(self, path: Path, project_folder: Path = None):
        if project_folder is None: project_folder = self.find_project_folder(path)
        if project_folder not in self.docs:
            self.docs[project_folder] = {}
        self.docs[project_folder][path] = TemplatedWooWooDocument(path, self.template_manager)
        self.doc_to_project[path] = project_folder

    def get_document(self, params):
        document_path = utils.uri_to_path(params.text_document.uri)

        if document_path in self.doc_to_project:
            return self.docs[self.doc_to_project[document_path]][document_path]
        else:
            return None

    def get_paths(self, document: TemplatedWooWooDocument = None):
        """Return paths to all documents known to the LS.
        If document parameter is provided, return only documents in the same project.
        """

        if document:
            return self.docs[self.doc_to_project[document.path]].keys()
        else:
            return self.doc_to_project.keys()

    def get_documents_from_project(self, document: TemplatedWooWooDocument):
        """
        Returns all TemplatedWooWooDocuments from the same project as "document".
        Args:
            document:

        Returns:

        """
        return self.docs[self.doc_to_project[document.path]].values()

    def delete_document(self, path: Path):
        del self.docs[self.doc_to_project[path]][path]

    def rename_document(self, old_path: Path, new_path: Path):
        old_project_folder = self.doc_to_project[old_path]
        new_project_folder = self.find_project_folder(new_path)

        if old_project_folder == new_project_folder:
            # Update the document within the same project
            self.docs[old_project_folder][new_path] = self.docs[old_project_folder].pop(old_path)
        else:
            # Move the document to a new project
            self.docs[new_project_folder][new_path] = self.docs[old_project_folder].pop(old_path)
            # Update the project mapping for the new path
            self.doc_to_project[new_path] = new_project_folder
            # Remove the old path from the project mapping
            del self.doc_to_project[old_path]

        # Update the path of the document
        self.docs[new_project_folder][new_path].path = new_path

    def handle_document_change(self, params: DidChangeTextDocumentParams):
        import time
        start_time = time.time()
        uri = params.text_document.uri
        path = utils.uri_to_path(uri)
        doc = self.workspace.get_document(uri)

        self.docs[self.doc_to_project[path]][path].update_source_incremental(doc, params)

        end_time = time.time()
        parse_duration = end_time - start_time
        #logger.debug(f"Parsing of {params.text_document.uri} took {parse_duration} seconds.")

    def set_template(self, template_file_path):
        # TODO: better fallback mechanisms and error handling + handle default template better
        if template_file_path != "":
            self.template_manager.load_template(template_file_path)
            self.analyzer.set_template(template_file_path)
        else:
            import utils
            self.template_manager.load_template(utils.get_absolute_path("templates/fit_math.yaml"))
            self.analyzer.set_template(utils.get_absolute_path("templates/fit_math.yaml"))

    def diagnose(self, doc_uri):
        diagnostics = self.analyzer.diagnose(WuffTextDocumentIdentifier(doc_uri))
        lsdiagnostics = []
        for diagnostic in diagnostics:
            lsdiagnostic = wuff_diagnostic_to_ls(diagnostic)
            lsdiagnostic.source = self.name
            lsdiagnostics.append(lsdiagnostic)

        self.publish_diagnostics(doc_uri, lsdiagnostics)



SERVER = WooWooLanguageServer('woowoo-language-SERVER', 'v0.1')


@SERVER.feature(INITIALIZE)
def initiliaze(ls: WooWooLanguageServer, params: InitializeParams) -> None:
    logger.debug("[INITIALIZE]")

    if len(params.workspace_folders) != 1:
        logger.error("Exactly one workspace has to be opened. No other options are supported for now.")

    # default: ""
    ls.set_template(params.initialization_options["templateFilePath"])

    ls.load_workspace(params.workspace_folders[0])


@SERVER.feature(INITIALIZED)
def initiliazed(_ls: WooWooLanguageServer, params: InitializedParams) -> None:
    logger.debug("[INITIALIZED] Connection was established.")


@SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: WooWooLanguageServer, params: DidOpenTextDocumentParams):
    logger.debug("[TEXT_DOCUMENT_DID_OPEN] SERVER.feature called")

    if ls.get_document(params) is None:
        document_path = utils.uri_to_path(params.text_document.uri)
        ls.load_document(document_path)

    ls.analyzer.open_document(WuffTextDocumentIdentifier(params.text_document.uri))
    ls.diagnose(params.text_document.uri)


@SERVER.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: WooWooLanguageServer, params: DidSaveTextDocumentParams) -> None:
    logger.debug("[TEXT_DOCUMENT_DID_SAVE] SERVER.feature called")

    ls.diagnose(params.text_document.uri)


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
        old_path, new_path = map(utils.uri_to_path, (old_uri, new_uri))
        if str(new_path).endswith(".woo"):
            ls.rename_document(old_path, new_path)
        else:
            ls.delete_document(old_path)



# TODO: Handle file deletion!

@SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: WooWooLanguageServer, params: DidChangeTextDocumentParams):
    logger.debug("[TEXT_DOCUMENT_DID_CHANGE] SERVER.feature called")
    doc_uri = params.text_document.uri
    doc = ls.workspace.get_document(params.text_document.uri)
    ls.analyzer.document_did_change(WuffTextDocumentIdentifier(doc_uri), doc.source)
    ls.diagnose(doc_uri)
    ls.handle_document_change(params)



@SERVER.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=Completer.trigger_characters))
def completions(ls: WooWooLanguageServer, params: LSCompletionParams):
    logger.debug("[TEXT_DOCUMENT_COMPLETION] SERVER.feature called")
    #return ls.completer.complete(params)
    params = completion_params_ls_to_wuff(params)
    completion_items_result = ls.analyzer.complete(params)
    items = [wuff_completion_item_to_ls(item) for item in completion_items_result]
    return CompletionList(is_incomplete=False, items=items)


@SERVER.feature(TEXT_DOCUMENT_HOVER)
def on_hover(ls: WooWooLanguageServer, params: TextDocumentPositionParams):
    logger.debug("[TEXT_DOCUMENT_HOVER] SERVER.feature called")
    result = ls.analyzer.hover(params.text_document.uri, params.position.line, params.position.character)
    content = MarkupContent(MarkupKind.Markdown, value=result)
    return Hover(contents=content)


@SERVER.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                SemanticTokensLegend(token_types=token_types,
                                     token_modifiers=token_modifiers))
def semantic_tokens(ls: WooWooLanguageServer, params: SemanticTokensParams):
    logger.debug("[TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL] SERVER.feature called")
    data = ls.analyzer.semantic_tokens(params.text_document.uri)
    return SemanticTokens(data=data)


@SERVER.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: WooWooLanguageServer, params: DefinitionParams):
    logger.debug("[TEXT_DOCUMENT_DEFINITION] SERVER.feature called")

    return ls.navigator.go_to_definition(params)


@SERVER.feature(TEXT_DOCUMENT_FOLDING_RANGE)
def folding_range(ls: WooWooLanguageServer, params: FoldingRangeParams):
    logger.debug("[TEXT_DOCUMENT_FOLDING_RANGE] SERVER.feature called")

    folding_ranges = ls.analyzer.folding_ranges(WuffTextDocumentIdentifier(params.text_document.uri))
    data = [wuff_folding_range_to_ls(item) for item in folding_ranges]
    return data



def start() -> None:
    SERVER.start_io()


if __name__ == "__main__":
    start()
