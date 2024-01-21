from tree_sitter import Language, Parser, Tree, Node
import os
import platform

from meta_context import MetaContext
from utils import get_absolute_path
from typing import List

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PARSERS_DIRECTORY = "tree-sitter/builds/"

def get_parser_lib_filename():
    filename = ""
    os_system = platform.system().lower()
    arch = platform.machine().lower()

    if arch in ["x64", "x86_64", "amd64"]:
        arch = "x64"
    elif arch in ["arm64"]:
        arch = "arm64"
    else:
        return None

    filename += os_system + "-" + arch
    if os_system == "windows":
        filename += ".dll"
    elif os_system == "linux":
        filename += ".so"
    else:
        return None

    return filename



def initialize_parsers():
    parser_filename = get_parser_lib_filename()
    loaded = False
    if parser_filename is not None:
        try:
            woowoo_lib_path = os.path.join(get_absolute_path(PARSERS_DIRECTORY + "woowoo/"), parser_filename)
            yaml_lib_path = os.path.join(get_absolute_path(PARSERS_DIRECTORY + "yaml/"), parser_filename)

            WOOWOO_LANGUAGE = Language(woowoo_lib_path, 'woowoo')
            YAML_LANGUAGE = Language(yaml_lib_path, 'yaml')
            loaded = True
        except OSError as e:
            logger.error(f"Error loading parser library: {e}")
            logger.error(f"Tried to load: {woowoo_lib_path} and {yaml_lib_path}")

    if not loaded:
        # unknown system, try to compile it locally
        logger.warning(f"Unsupported system, falling back to local compilation (C++ compiler needed).")
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


def parse_source(src: str) -> (Tree, List[MetaContext]):
    tree = woowoo_parser.parse(bytes(src, "utf-8"))

    yaml_trees = parse_metas(tree)

    return tree, yaml_trees

def parse_metas(tree: Tree) -> List[MetaContext]:
    query = WOOWOO_LANGUAGE.query("(meta_block) @yaml")
    meta_blocks = query.captures(tree.root_node)

    yaml_trees = []
    for meta_block, _ in meta_blocks:
        parent = meta_block.parent
        parent_name = extract_structure_name(parent)
        parent_type = parent.type if "outer_environment" not in parent.type else "outer_environment"
        yaml_tree = yaml_parser.parse(meta_block.text)
        yaml_trees.append(MetaContext(yaml_tree, meta_block.start_point[0], parent_type, parent_name))

    return yaml_trees

def extract_structure_name(node: Node):
    """
    Extract the name part of a given node.
    """
    child_with_name = None
    if node.type == "document_part":
        child_with_name = "document_part_title"
    elif "outer_environment" in node.type:
        child_with_name = "outer_environment_type"
    elif node.type == "object":
        child_with_name = "object_type"

    if child_with_name is None:
        return None

    for child in node.children:
        if child.type == child_with_name:
            return child.text.decode('utf-8')