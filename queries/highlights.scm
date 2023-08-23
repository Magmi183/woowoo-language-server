; Comment
; TODO

; Include statement

(include) @keyword
(filename) @string


; Document part

(document_part "." @operator)
(document_part_type) @keyword
(document_part_title) @string

; Meta block
; TODO: Should I highlight the whole metablock? Is it better than nothing?


; Object
(object ["." ":"] @operator)
(object_type) @property


; Block

;  - Short Inner Environment

(short_inner_environment ["." ":"] @operator)
(short_inner_environment_type) @type

;  - Verbose Inner Environment

(verbose_inner_environment (_ "\"" @string))
(verbose_inner_environment (_ ["." "@" "#"] @operator))
(verbose_inner_environment_type) @type
(verbose_inner_environment_at_type) @type

;  - Outer Environment

(outer_environment_type) @type
(fragile_outer_environment ["!" ":"] @operator)
(classic_outer_environment ["." ":"] @operator)

;  - Math

(math_environment "$" @function)
(math_environment_body ) @variable
