import logging
from pygls.server import LanguageServer

from completer import Completer
from hoverer import Hoverer
from parser import parse_source

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionParams, TEXT_DOCUMENT_HOVER, TextDocumentPositionParams,
    DidOpenTextDocumentParams, DidChangeTextDocumentParams, TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_CHANGE,
    CompletionOptions, INITIALIZED,
)

# TODO: Setup logging better.
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WooWooLanguageServer(LanguageServer):

    def __init__(self, name: str, version: str):
        logger.debug("Constructing WooWooLanguageServer.")
        super().__init__(name, version)

        self.tree = None

        self.completer = Completer(self)
        self.hoverer = Hoverer(self)


SERVER = WooWooLanguageServer('woowoo-language-SERVER', 'v0.1')


@SERVER.feature(INITIALIZED)
def initiliazed(_ls: WooWooLanguageServer, params) -> None:
    logger.debug("[INITIALIZED] Connection was established.")


@SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: WooWooLanguageServer, params: DidOpenTextDocumentParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_DID_OPEN")
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    ls.tree = parse_source(doc.source)


@SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: WooWooLanguageServer, params: DidChangeTextDocumentParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_DID_CHANGE")
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)
    ls.tree = parse_source(doc.source)


# TODO: Set trigger characters.
@SERVER.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=['.']))
def completions(ls: WooWooLanguageServer, params: CompletionParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_COMPLETION")
    return ls.completer.complete(params)


@SERVER.feature(TEXT_DOCUMENT_HOVER)
def on_hover(ls: WooWooLanguageServer, params: TextDocumentPositionParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_HOVER")
    return ls.hoverer.hover(params)


SERVER.start_tcp('127.0.0.1', 8080)
