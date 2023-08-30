from tree_sitter import Language, Parser, Tree
from pathlib import Path

ls_path = Path(__file__).resolve().parent
WOOWOO_LANGUAGE = Language(
    library_path=Path.joinpath(ls_path, Path("woowoo-parser.so")).as_posix(), name="woowoo"
)

YAML_LANGUAGE = Language(
    library_path=Path.joinpath(ls_path, Path("yaml-parser.so")).as_posix(), name="yaml"
)

woowoo_parser = Parser()
woowoo_parser.set_language(WOOWOO_LANGUAGE)

yaml_parser = Parser()
yaml_parser.set_language(YAML_LANGUAGE)

def parse_source(src: str) -> (Tree, [(int, Tree)]):
    tree = woowoo_parser.parse(bytes(src, "utf-8"))

    query = WOOWOO_LANGUAGE.query("(meta_block) @yaml")
    meta_blocks = query.captures(tree.root_node)

    yaml_trees = [] # (line offset, tree)
    for meta_block in meta_blocks:
        yaml_tree = yaml_parser.parse(meta_block[0].text)
        yaml_trees.append((meta_block[0].start_point[0],yaml_tree))


    return tree, yaml_trees
