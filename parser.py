from tree_sitter import Language, Parser, Tree
import os
from ctypes import CDLL, c_char_p
import ctypes.util
import sys
import platform
from utils import get_absolute_path

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_parser_lib_filename():
    os_system = platform.system()

    if os_system == "Windows":
        return "parser-windows.dll"
    elif os_system == "Linux":
        return "parser-linux.so"
    else:
        return None

def initialize_parsers():
    parser_filename = get_parser_lib_filename()
    if parser_filename is not None:
        try:
            woowoo_lib_path = os.path.join(get_absolute_path('builds_ts/woowoo'), parser_filename)
            yaml_lib_path = os.path.join(get_absolute_path('builds_ts/yaml'), parser_filename)

            WOOWOO_LANGUAGE = Language(woowoo_lib_path, 'woowoo')
            YAML_LANGUAGE = Language(yaml_lib_path, 'yaml')
        except OSError as e:
            # Log the error details
            logger.error(f"Error loading parser library: {e}")
            logger.error(f"Tried to load: {woowoo_lib_path} and {yaml_lib_path}")
            # Handle the error (e.g., fall back to compilation)
            return
    else:
        # unknown system, try to compile it locally
        WOOWOO_LANGUAGE, YAML_LANGUAGE = compile_parsers()

    woowoo_parser = Parser()
    woowoo_parser.set_language(WOOWOO_LANGUAGE)
    yaml_parser = Parser()
    yaml_parser.set_language(YAML_LANGUAGE)

    return woowoo_parser, WOOWOO_LANGUAGE, yaml_parser, YAML_LANGUAGE



def compile_parsers():
    woowoo_path = get_absolute_path('tree-sitter/tree-sitter-woowoo')
    yaml_path = get_absolute_path('tree-sitter/tree-sitter-yaml')
    Language.build_library(
        get_absolute_path('build/my-languages.so'),
        [woowoo_path, yaml_path]
    )
    WOOWOO_LANGUAGE = Language(get_absolute_path('build/my-languages.so'), 'woowoo')
    YAML_LANGUAGE = Language(get_absolute_path('build/my-languages.so'), 'yaml')


    return WOOWOO_LANGUAGE, YAML_LANGUAGE


woowoo_parser, WOOWOO_LANGUAGE, yaml_parser, YAML_LANGUAGE = initialize_parsers()


def parse_source(src: str) -> (Tree, [(int, Tree)]):
    tree = woowoo_parser.parse(bytes(src, "utf-8"))

    query = WOOWOO_LANGUAGE.query("(meta_block) @yaml")
    meta_blocks = query.captures(tree.root_node)

    yaml_trees = [] # [(line offset, tree)]
    for meta_block in meta_blocks:
        yaml_tree = yaml_parser.parse(meta_block[0].text)
        yaml_trees.append((meta_block[0].start_point[0], yaml_tree))

    return tree, yaml_trees
