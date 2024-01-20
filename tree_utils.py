from typing import Optional, Union

from tree_sitter import Node

from parser import WOOWOO_LANGUAGE

def build_query_string_from_list(node_type_list, capture_name):
    formatted_nodes = [f"({node})" for node in node_type_list]
    query_string = f"[ {' '.join(formatted_nodes)} ] @{capture_name}"

    return query_string


def is_query_overlapping_pos(tree, query, line, col, lang = WOOWOO_LANGUAGE) -> bool:
    nodes = lang.query(query).captures(tree.root_node, start_point=(line, col), end_point=(line, col+1))    

    return len(nodes) > 0


def get_child_by_type(node: Node, child_type: str, text = False) -> Union[Node, str, None]:
    for child in node.children:
        if child.type == child_type:
            if not text:
                return child
            else:
                return child.text.decode("utf-8")

    return None