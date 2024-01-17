import logging
from pathlib import Path

from pygls.server import LanguageServer

import utils
from completer import Completer
from folder import Folder
from highlighter import Highlighter
from hoverer import Hoverer
from linter import Linter
from navigator import Navigator

from template_manager.template_manager import TemplateManager

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionParams, TEXT_DOCUMENT_HOVER, TextDocumentPositionParams,
    DidOpenTextDocumentParams, DidChangeTextDocumentParams, TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_CHANGE,
    CompletionOptions, INITIALIZED, TEXT_DOCUMENT_DEFINITION, TEXT_DOCUMENT_DID_SAVE,
    DidSaveTextDocumentParams, TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SemanticTokensParams,
    SemanticTokensLegend, InitializedParams, InitializeParams, INITIALIZE,
    WorkspaceFolder, DefinitionParams, TEXT_DOCUMENT_FOLDING_RANGE, FoldingRangeParams, WORKSPACE_DID_RENAME_FILES,
    RenameFilesParams, WORKSPACE_WILL_RENAME_FILES
)

from woowoodocument import WooWooDocument

# TODO: Setup logging better.
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WooWooLanguageServer(LanguageServer):

    def __init__(self, name: str, version: str):
        logger.debug("Constructing WooWooLanguageServer.")
        super().__init__(name, version)

        self.template_manager = TemplateManager()

        self.linter = Linter(self)
        self.completer = Completer(self)
        self.hoverer = Hoverer(self)
        self.highlighter = Highlighter(self)
        self.navigator = Navigator(self)
        self.folder = Folder(self)

        self.docs = {}

    def load_workspace(self, workspace: WorkspaceFolder):
        root_path = utils.uri_to_path(workspace.uri)
        woo_files = root_path.rglob('*.woo')

        for woo_file in woo_files:
            self.load_document(woo_file)

    def load_document(self, path: Path):
        self.docs[path] = WooWooDocument(path)

    def get_document(self, params):
        document_path = utils.uri_to_path(params.text_document.uri)
        return self.docs.get(document_path)

    def delete_document(self, path: Path):
        del self.docs[path]

    def rename_document(self, old_path: Path, new_path: Path):
        self.docs[new_path] = self.docs[old_path]
        self.delete_document(old_path)

    def set_template(self, template_file_path):
        # TODO: better fallback mechanisms and error handling + handle default template better
        if template_file_path != "":
            self.template_manager.load_template(template_file_path)
        else:
            import utils
            self.template_manager.load_template(utils.get_absolute_path("template_sandbox/fit_math.yaml"))

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

    ls.linter.diagnose(params)


@SERVER.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: WooWooLanguageServer, params: DidSaveTextDocumentParams) -> None:
    logger.debug("[TEXT_DOCUMENT_DID_SAVE] SERVER.feature called")

    ls.linter.diagnose(params)


@SERVER.feature(WORKSPACE_WILL_RENAME_FILES)
def will_rename_files(ls: WooWooLanguageServer, params: RenameFilesParams):
    logger.debug("[WORKSPACE_WILL_RENAME_FILES] SERVER.feature called")

    # TODO: Refactor file references to the new name (like in .include statements)
    # https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#renameFilesParams


@SERVER.feature(WORKSPACE_DID_RENAME_FILES)
def did_rename_files(ls: WooWooLanguageServer, params: RenameFilesParams):
    logger.debug("[WORKSPACE_DID_RENAME_FILES] notification received")

    for file_rename in params.files:
        old_uri, new_uri = file_rename.old_uri, file_rename.new_uri
        old_path, new_path = map(utils.uri_to_path, (old_uri, new_uri))
        if str(new_path).endswith(".woo"):
            ls.rename_document(old_path, new_path)
        else:
            ls.delete_document(old_path)



# TODO: Handle file deletion!

@SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: WooWooLanguageServer, params: DidChangeTextDocumentParams):
    logger.debug("[TEXT_DOCUMENT_DID_CHANGE] SERVER.feature called")
    uri = params.text_document.uri
    path = utils.uri_to_path(uri)
    doc = ls.workspace.get_document(uri)

    # NOTE: As of now, re-parsing the whole file on every change.
    ls.docs[path].update_source(doc.source)

    ls.linter.diagnose(params)


@SERVER.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=Completer.trigger_characters))
def completions(ls: WooWooLanguageServer, params: CompletionParams):
    logger.debug("[TEXT_DOCUMENT_COMPLETION] SERVER.feature called")
    return ls.completer.complete(params)


""" 
# TODO: Uncomment when the feature is finished.
@SERVER.feature(TEXT_DOCUMENT_HOVER)
def on_hover(ls: WooWooLanguageServer, params: TextDocumentPositionParams):
    logger.debug("[TEXT_DOCUMENT_HOVER] SERVER.feature called")
    return ls.hoverer.hover(params)
"""


@SERVER.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                SemanticTokensLegend(token_types=Highlighter.token_types,
                                     token_modifiers=Highlighter.token_modifiers))
def semantic_tokens(ls: WooWooLanguageServer, params: SemanticTokensParams):
    logger.debug("[TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL] SERVER.feature called")
    return ls.highlighter.semantic_tokens(params)


@SERVER.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: WooWooLanguageServer, params: DefinitionParams):
    logger.debug("[TEXT_DOCUMENT_DEFINITION] SERVER.feature called")

    return ls.navigator.go_to_definition(params)


@SERVER.feature(TEXT_DOCUMENT_FOLDING_RANGE)
def folding_range(ls: WooWooLanguageServer, params: FoldingRangeParams):
    logger.debug("[TEXT_DOCUMENT_FOLDING_RANGE] SERVER.feature called")

    return ls.folder.folding_ranges(params)


def start() -> None:
    SERVER.start_io()


if __name__ == "__main__":
    start()
