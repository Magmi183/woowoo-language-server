import logging
import re
from pygls.server import LanguageServer

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
    SemanticTokensLegend, InitializedParams, InitializeParams, InitializeResult, ServerCapabilities, INITIALIZE
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
        self.utf8_to_utf16_mappings = None

        self.linter = Linter(self)
        self.completer = Completer(self)
        self.hoverer = Hoverer(self)
        self.highlighter = Highlighter(self)

    def utf8_char_len(self, first_byte):
        """Determine UTF-8 character length based on the first byte."""
        if first_byte < 0b10000000:
            return 1
        elif first_byte < 0b11100000:
            return 2
        elif first_byte < 0b11110000:
            return 3
        else:
            return 4

    def build_utf8_to_utf16_mapping(self, source):
        lines = source.splitlines()
        mappings = []

        for line in lines:
            utf8_offset = 0
            utf16_position = 0
            line_mapping = {}

            utf8_bytes = line.encode('utf-8')

            while utf8_offset < len(utf8_bytes):
                # Decode one character at a time
                char_len = self.utf8_char_len(utf8_bytes[utf8_offset])

                # Directly compute the length of the character in UTF-16 units
                utf16_len = len(utf8_bytes[utf8_offset:utf8_offset + char_len].decode('utf-8').encode('utf-16-le')) // 2
                utf16_position += utf16_len

                # Record the mapping
                for i in range(char_len):
                    line_mapping[utf8_offset + i] = utf16_position - (utf16_len - i)

                utf8_offset += char_len

            mappings.append(line_mapping)

        self.utf8_to_utf16_mappings = mappings

    def utf8_to_utf16_offset(self, coords):
        """Converts a line's utf8 offset to its utf16 offset using the mapping"""
        line_num, utf8_offset = coords
        return line_num, self.utf8_to_utf16_mappings[line_num].get(utf8_offset, utf8_offset)


SERVER = WooWooLanguageServer('woowoo-language-SERVER', 'v0.1')


@SERVER.feature(INITIALIZED)
def initiliazed(_ls: WooWooLanguageServer, params: InitializedParams) -> None:
    logger.debug("[INITIALIZED] Connection was established.")


@SERVER.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: WooWooLanguageServer, params: DidOpenTextDocumentParams):
    logger.debug("SERVER.feature called: TEXT_DOCUMENT_DID_OPEN")
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)

    ls.tree = parse_source(doc.source)
    ls.build_utf8_to_utf16_mapping(doc.source)

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
    doc = ls.workspace.get_document(uri)

    ls.tree = parse_source(doc.source)
    ls.build_utf8_to_utf16_mapping(doc.source)

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
    return ls.highlighter.semantic_tokens()


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
