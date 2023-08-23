import logging
import re
from pygls.server import LanguageServer

import utils
from completer import Completer
from highlighter import Highlighter
from hoverer import Hoverer
from linter import Linter
from parser import parse_source

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionParams, TEXT_DOCUMENT_HOVER, TextDocumentPositionParams,
    DidOpenTextDocumentParams, DidChangeTextDocumentParams, TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_CHANGE,
    CompletionOptions, INITIALIZED, TEXT_DOCUMENT_DEFINITION, Location, Position, Range, TEXT_DOCUMENT_DID_SAVE,
    DidSaveTextDocumentParams, TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SemanticTokensParams, SemanticTokens,
    SemanticTokensLegend, InitializedParams, InitializeParams, InitializeResult, ServerCapabilities, INITIALIZE,
    WorkspaceFolder
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

        self.linter = Linter(self)
        self.completer = Completer(self)
        self.hoverer = Hoverer(self)
        self.highlighter = Highlighter(self)

        self.docs = {}

    def load_workspace(self, workspace: WorkspaceFolder):
        root_path = utils.uri_to_path(workspace.uri)
        for woo_file in root_path.rglob('*.woo'):
            self.docs[woo_file] = WooWooDocument(woo_file)


SERVER = WooWooLanguageServer('woowoo-language-SERVER', 'v0.1')


@SERVER.feature(INITIALIZE)
def initiliaze(ls: WooWooLanguageServer, params: InitializeParams) -> None:
    logger.debug("[INITIALIZE]")

    if len(params.workspace_folders) != 1:
        logger.error("Exactly one workspace has to be opened. No other options are supported for now.")

    ls.load_workspace(params.workspace_folders[0])


@SERVER.feature(INITIALIZED)
def initiliazed(_ls: WooWooLanguageServer, params: InitializedParams) -> None:
    logger.debug("[INITIALIZED] Connection was established.")


@SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: WooWooLanguageServer, params: DidOpenTextDocumentParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_DID_OPEN")

    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    ls.linter.diagnose(doc)


@SERVER.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: WooWooLanguageServer, params: DidSaveTextDocumentParams) -> None:
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_DID_SAVE")

    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    ls.linter.diagnose(doc)


@SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: WooWooLanguageServer, params: DidChangeTextDocumentParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_DID_CHANGE")
    uri = params.text_document.uri
    path = utils.uri_to_path(uri)

    # NOTE: As of now, re-parsing the whole file on every change.
    ls.docs[path] = WooWooDocument(path)

    doc = ls.workspace.get_document(uri)
    ls.linter.diagnose(doc)


# TODO: Set trigger characters.
@SERVER.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=Completer.trigger_characters))
def completions(ls: WooWooLanguageServer, params: CompletionParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_COMPLETION")
    return ls.completer.complete(params)


@SERVER.feature(TEXT_DOCUMENT_HOVER)
def on_hover(ls: WooWooLanguageServer, params: TextDocumentPositionParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_HOVER")
    return ls.hoverer.hover(params)


@SERVER.feature(TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                SemanticTokensLegend(token_types=Highlighter.token_types,
                                     token_modifiers=Highlighter.token_modifiers))
def semantic_tokens(ls: WooWooLanguageServer, params: SemanticTokensParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL")

    # NOTE: At this time, this function is used to full-scale highlighting.
    # That means no syntax highlighting is needed on the client side.

    return ls.highlighter.semantic_tokens(params)


"""
# TODO:
@SERVER.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: WooWooLanguageServer, params: TextDocumentPositionParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_DEFINITION")

    return Location(params.text_document.uri, Range(
        start=Position(line=max(0, 0), character=max(0, 0)),
        end=Position(line=max(0, 0), character=max(0, 0)),
    ))
"""

SERVER.start_tcp('127.0.0.1', 8080)
