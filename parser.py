from tree_sitter import Language, Parser, Tree
from pathlib import Path

from utils import get_absolute_path

# Use the function to get the absolute paths
woowoo_path = get_absolute_path('tree-sitter/tree-sitter-woowoo')
yaml_path = get_absolute_path('tree-sitter/tree-sitter-yaml')

# Build the library
Language.build_library(
    get_absolute_path('build/my-languages.so'),
    [woowoo_path, yaml_path]
)

# Initialize languages
WOOWOO_LANGUAGE = Language(get_absolute_path('build/my-languages.so'), 'woowoo')
YAML_LANGUAGE = Language(get_absolute_path('build/my-languages.so'), 'yaml')


woowoo_parser = Parser()
woowoo_parser.set_language(WOOWOO_LANGUAGE)

yaml_parser = Parser()
yaml_parser.set_language(YAML_LANGUAGE)

def parse_source(src: str) -> (Tree, [(int, Tree)]):
    tree = woowoo_parser.parse(bytes(src, "utf-8"))

    query = WOOWOO_LANGUAGE.query("(meta_block) @yaml")
    meta_blocks = query.captures(tree.root_node)

    yaml_trees = [] # [(line offset, tree)]
    for meta_block in meta_blocks:
        yaml_tree = yaml_parser.parse(meta_block[0].text)
        yaml_trees.append((meta_block[0].start_point[0], yaml_tree))

    return tree, yaml_trees
