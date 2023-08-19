import logging
from pygls.server import LanguageServer

from hoverer import Hoverer
from parser import parse_source

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    CompletionParams, TEXT_DOCUMENT_HOVER, TextDocumentPositionParams, MarkupContent, MarkupKind, Hover,
    DidOpenTextDocumentParams, DidChangeTextDocumentParams, TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_CHANGE,
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

        self.hoverer = Hoverer(self)



SERVER = WooWooLanguageServer('woowoo-language-SERVER', 'v0.1')


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


@SERVER.feature(TEXT_DOCUMENT_HOVER)
def on_hover(ls: WooWooLanguageServer, params: TextDocumentPositionParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_HOVER")
    return ls.hoverer.hover(params)


SERVER.start_tcp('127.0.0.1', 8080)
