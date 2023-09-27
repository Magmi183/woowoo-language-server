; TOOK FROM: https://github.com/nvim-treesitter/nvim-treesitter/blob/master/queries/yaml/highlights.scm
; types were changed though, to reflect valid VSCode types

(boolean_scalar) @enum
(null_scalar) @keyword
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
] @macro

; I COMMENTED THIS, because some nodes were retrieved multiple times (as result of previous queries)
;(block_mapping_pair
;  key: (flow_node [(double_quote_scalar) (single_quote_scalar)] @variable))
;(block_mapping_pair
;  key: (flow_node (plain_scalar (string_scalar) @variable)))

;(flow_mapping
;  (_ key: (flow_node [(double_quote_scalar) (single_quote_scalar)] @variable)))
;(flow_mapping
;  (_ key: (flow_node (plain_scalar (string_scalar) @variable))))

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