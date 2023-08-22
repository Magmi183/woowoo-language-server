
def build_query_string_from_list(node_type_list, capture_name):
    formatted_nodes = [f"({node})" for node in node_type_list]
    query_string = f"[ {' '.join(formatted_nodes)} ] @{capture_name}"

    return query_string
