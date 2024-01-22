from pathlib import Path

from lsprotocol.types import DidChangeTextDocumentParams
from pygls.workspace import Document

from meta_context import MetaContext
from parser import parse_source
from typing import List


class WooWooDocument:

    def __init__(self, path: Path):
        self.path = path
        self.tree = None
        self.meta_blocks: List[MetaContext] = []
        self.comment_lines = []
        self.utf8_to_utf16_mappings = None
        self._load()

    def update_source(self, source: str):
        self.tree, self.meta_blocks = parse_source(source)
        self.build_mappings(source)
        self.update_comment_lines(source)

    def update_source_incremental(self, document: Document, params: DidChangeTextDocumentParams):
        changed_lines = set()
        for change in params.content_changes:
            for line_number in range(change.range.start.line, change.range.end.line + 1):
                changed_lines.add(line_number)
            # TODO: fix this incremental part
            """
            start_byte = document.offset_at_position(change.range.start)
            old_end_byte = document.offset_at_position(change.range.end)
            new_end_byte = start_byte + len(change.text.encode('utf-8'))

            start_point = self.utf16_to_utf8_offset((change.range.start.line, change.range.start.character))
            old_end_point = self.utf16_to_utf8_offset((change.range.end.line, change.range.end.character))
            new_end_point = (old_end_point[0], old_end_point[1] + len(change.text))

            # Debug logging
            logging.debug(f"Edit: start_byte={start_byte}, old_end_byte={old_end_byte}, new_end_byte={new_end_byte}, "
                  f"start_point={start_point}, old_end_point={old_end_point}, new_end_point={new_end_point}")

            self.tree.edit(
                start_byte=start_byte,
                old_end_byte=old_end_byte,
                new_end_byte=new_end_byte,
                start_point=start_point,
                old_end_point=old_end_point,
                new_end_point=new_end_point
            )

        self.tree = woowoo_parser.parse(bytes(document.source, "utf-8"), old_tree=self.tree)
        self.meta_blocks = parse_metas(self.tree)
        """

        self.update_comments_and_mappings(document.source, changed_lines)

        # TODO: remove when incremental fixed
        self.tree, self.meta_blocks = parse_source(document.source)

    def _load(self):
        # TODO: Support more encodings and test this.
        with self.path.open('r', encoding='utf-8') as f:
            source = f.read()
            self.update_source(source)


    def update_comments_and_mappings(self, source, changed_lines):
        self.comment_lines.clear()
        first_change = min(changed_lines)
        lines = source.splitlines()
        max_line_index = len(lines) - 1

        for i, line in enumerate(lines):
            if line.startswith("%"):
                self.comment_lines.append((i, len(line)))

            if i < first_change:
                continue

            if i < len(self.utf8_to_utf16_mappings):
                # Update existing mapping
                self.utf8_to_utf16_mappings[i] = self.line_utf8_to_utf16_mapping(line)
            else:
                # Append mapping for new line
                self.utf8_to_utf16_mappings.append(self.line_utf8_to_utf16_mapping(line))

        # remove outdated
        self.utf8_to_utf16_mappings = self.utf8_to_utf16_mappings[:max_line_index + 1]

        # Update utf16_to_utf8_mappings only for changed lines and beyond
        for i in range(first_change, len(self.utf8_to_utf16_mappings)):
            inverse_mapping = {v: k for k, v in self.utf8_to_utf16_mappings[i].items()}
            if i < len(self.utf16_to_utf8_mappings):
                self.utf16_to_utf8_mappings[i] = inverse_mapping
            else:
                self.utf16_to_utf8_mappings.append(inverse_mapping)
        # remove outdated
        self.utf16_to_utf8_mappings = self.utf16_to_utf8_mappings[:max_line_index + 1]

    def update_comment_lines(self, source):
        self.comment_lines.clear()
        for i, line in enumerate(source.splitlines()):
            if line.startswith("%"):
                self.comment_lines.append((i, len(line)))


    def build_mappings(self, source):
        self.build_utf8_to_utf16_mapping(source)
        self.utf16_to_utf8_mappings = [{v: k for k, v in m.items()} for m in self.utf8_to_utf16_mappings]


    def build_utf8_to_utf16_mapping(self, source):
        lines = source.splitlines()
        mappings = []

        for line in lines:
            mappings.append(self.line_utf8_to_utf16_mapping(line))

        self.utf8_to_utf16_mappings = mappings

    def line_utf8_to_utf16_mapping(self, line):
        utf8_offset = 0
        utf16_position = 0
        line_mapping = {}

        utf8_bytes = line.encode('utf-8')

        while utf8_offset < len(utf8_bytes):
            # Decode one character at a time
            char_len = WooWooDocument.utf8_char_len(utf8_bytes[utf8_offset])

            # Directly compute the length of the character in UTF-16 units
            utf16_len = len(utf8_bytes[utf8_offset:utf8_offset + char_len].decode('utf-8').encode('utf-16-le')) // 2
            utf16_position += utf16_len

            # Record the mapping
            for i in range(char_len):
                line_mapping[utf8_offset + i] = utf16_position - (utf16_len - i)

            utf8_offset += char_len

        return line_mapping

    @staticmethod
    def utf8_char_len(first_byte):
        """Determine UTF-8 character length based on the first byte."""
        if first_byte < 0b10000000:
            return 1
        elif first_byte < 0b11100000:
            return 2
        elif first_byte < 0b11110000:
            return 3
        else:
            return 4

    def utf8_to_utf16_offset(self, coords):
        """Converts a line's utf8 offset to its utf16 offset using the mapping.
        This is needed because VSCode uses utf16 internally, it is based on JavaScript.
        https://github.com/microsoft/vscode-languageserver-node/issues/1224"""
        line_num, utf8_offset = coords

        # add {} default for rare cases (like empty lines at the end being ignored)
        mapping = self.utf8_to_utf16_mappings[line_num] if 0 <= line_num < len(self.utf8_to_utf16_mappings) else {}
        return line_num, mapping.get(utf8_offset, utf8_offset)

    
    def utf16_to_utf8_offset(self, coords):
        """
        First column = 0. In VSCode however, first = 1, so subtraction has to be done before calling this function.
        """
        line_num, utf16_offset = coords

        if 0 <= line_num < len(self.utf16_to_utf8_mappings):
            return line_num, self.utf16_to_utf8_mappings[line_num].get(utf16_offset, 0)
        else:
            # in this case, return best guess, which is coords
            # this will occur very rarely, for example pasting new content
            return coords