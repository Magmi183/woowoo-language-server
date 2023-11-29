from pathlib import Path

from parser import parse_source

class WooWooDocument:

    def __init__(self, path: Path):
        self.path = path
        self.tree = None
        self.source = None
        self.meta_block_trees = [] # [(line offset, tree)]
        self.comment_lines = []
        self.utf8_to_utf16_mappings = None
        self._load()

    def update_source(self, source: str):
        self.source = source
        self.tree, self.meta_block_trees = parse_source(source)
        self.build_utf8_to_utf16_mapping(source)
        self.update_comment_lines()

    def _load(self):
        # TODO: Support more encodings and test this.
        with self.path.open('r', encoding='utf-8') as f:
            source = f.read()
            self.update_source(source)
    
    def update_comment_lines(self):
        self.comment_lines.clear()
        for i, line in enumerate(self.source.split("\n")):
            if len(line) > 0 and line[0] == "%":
                self.comment_lines.append((i, len(line)))
            

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
                char_len = WooWooDocument.utf8_char_len(utf8_bytes[utf8_offset])

                # Directly compute the length of the character in UTF-16 units
                utf16_len = len(utf8_bytes[utf8_offset:utf8_offset + char_len].decode('utf-8').encode('utf-16-le')) // 2
                utf16_position += utf16_len

                # Record the mapping
                for i in range(char_len):
                    line_mapping[utf8_offset + i] = utf16_position - (utf16_len - i)

                utf8_offset += char_len

            mappings.append(line_mapping)

        self.utf8_to_utf16_mappings = mappings

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
        """Converts a line's utf8 offset to its utf16 offset using the mapping"""
        line_num, utf8_offset = coords

        # add {} default for rare cases (like empty lines at the end being ignored)
        mapping = self.utf8_to_utf16_mappings[line_num] if 0 <= line_num < len(self.utf8_to_utf16_mappings) else {}
        return line_num, mapping.get(utf8_offset, utf8_offset)