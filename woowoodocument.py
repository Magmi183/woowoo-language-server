from pathlib import Path

from parser import parse_source, YAML_LANGUAGE
from template_manager.reference import Reference


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
        self.build_mappings(source)
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


    def build_mappings(self, source):
        self.build_utf8_to_utf16_mapping(source)
        self.utf16_to_utf8_mappings = [{v: k for k, v in m.items()} for m in self.utf8_to_utf16_mappings]


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


    def search_meta_blocks(self, reference: Reference):
        """Search for all k:v pairs in meta blocks that follow the structure in reference.
         Collect all values and return them."""

        query = f"""(block_mapping_pair
            key: (flow_node [(double_quote_scalar) (single_quote_scalar) (plain_scalar)] @key)
            value: (flow_node) @value
            (#eq? @key "{reference.meta_key}"))"""
        nodes_all = []
        for meta_block in self.meta_block_trees:
            nodes_all += YAML_LANGUAGE.query(query).captures(meta_block[1].root_node)

        values = set()
        for node in nodes_all:
            if node[1] == 'value':
                values.add(node[0].text)

        return values


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
            return line_num, self.utf16_to_utf8_mappings[line_num][utf16_offset]
        else:
            pass
            # TODO shallnot happen