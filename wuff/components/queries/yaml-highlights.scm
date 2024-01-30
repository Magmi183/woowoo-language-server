; Queries are from https://github.com/nvim-treesitter/nvim-treesitter/blob/master/queries/yaml/highlights.scm , but the order of queries was changed.
; The order of the query reflects the priority - if a given node is retrieved by multiple queries,
; the type that counts is the type given by the first query that retrieved the given node.

(block_mapping_pair
  key: (flow_node [(double_quote_scalar) (single_quote_scalar)] @property))
(block_mapping_pair
  key: (flow_node (plain_scalar (string_scalar) @property)))

(flow_mapping
  (_ key: (flow_node [(double_quote_scalar) (single_quote_scalar)] @property)))
(flow_mapping
  (_ key: (flow_node (plain_scalar (string_scalar) @property))))

(boolean_scalar) @keyword
(null_scalar) @enum
(double_quote_scalar) @string
(single_quote_scalar) @string
((block_scalar) @string (#set! "priority" 99))
(string_scalar) @string
(escape_sequence) @string
(integer_scalar) @number
(float_scalar) @number
(comment) @comment
(anchor_name) @type
(alias_name) @type
(tag) @type

[
  (yaml_directive)
  (tag_directive)
  (reserved_directive)
] @modifier

[
 ","
 "-"
 ":"
 ">"
 "?"
 "|"
] @operator

[
 "["
 "]"
 "{"
 "}"
] @operator

[
 "*"
 "&"
 "---"
 "..."
] @operator
