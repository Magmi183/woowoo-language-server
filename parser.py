from tree_sitter import Language, Parser, Tree
from pathlib import Path

ls_path = Path(__file__).resolve().parent
WOOWOO_LANGUAGE = Language(
    library_path=Path.joinpath(ls_path, Path("woowoo-parser.so")).as_posix(), name="woowoo"
)

parser = Parser()
parser.set_language(WOOWOO_LANGUAGE)


def parse_source(src: str) -> Tree:
    tree = parser.parse(bytes(src, "utf-8"))
    return tree
