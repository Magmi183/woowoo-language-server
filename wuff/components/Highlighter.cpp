//
// Created by Michal Janecek on 30.01.2024.
//

#include "Highlighter.h"

const std::vector<std::string> Highlighter::tokenTypes = {
        "namespace", "type", "class", "enum", "interface", "struct", "typeParameter",
        "parameter", "variable", "variable.other", "storage.type.struct", "property",
        "enumMember", "event", "function", "method", "macro", "keyword", "modifier",
        "comment", "string", "number", "regexp", "operator", "decorator"
};

const std::vector<std::string> Highlighter::tokenModifiers = {
        "declaration", "definition", "readonly", "static", "deprecated",
        "abstract", "async", "modification", "documentation", "defaultLibrary"
};

Highlighter::Highlighter(WooWooAnalyzer* analyzer) : analyzer(analyzer) {}

std::vector<int> Highlighter::semanticTokens(const std::string &documentPath) {
    WooWooDocument * document = analyzer->getDocument(documentPath);

    std::vector<int> data;

    uint32_t error_offset;
    TSQueryError error_type;
    TSQuery* query = ts_query_new(tree_sitter_woowoo(), woowooHighlightQueries.c_str(), woowooHighlightQueries.size(), &error_offset, &error_type);
    TSQueryCursor* wooCursor = ts_query_cursor_new();
    ts_query_cursor_exec(wooCursor, query, ts_tree_root_node(document->tree));
    
    std::vector<TSNode> metaBlocksNodes = getMetaBlocksNodes(document);
    
    
    return data;
}


std::vector<TSNode> Highlighter::getMetaBlocksNodes(WooWooDocument *document) {
    std::vector<TSNode> metaBlocksNodes;

    uint32_t error_offset;
    TSQueryError error_type;
    for(MetaContext * metaContext : document->metaBlocks){
        TSQuery* metaQuery = ts_query_new(tree_sitter_yaml(), yamlHighlightQueries.c_str(),yamlHighlightQueries.size(), &error_offset, &error_type);
        TSQueryCursor* yamlCursor = ts_query_cursor_new();
        ts_query_cursor_exec(yamlCursor, metaQuery, ts_tree_root_node(metaContext->tree));

        TSQueryMatch match;
        std::string nodeType;
        std::string nodeText;
        if (ts_query_cursor_next_match(yamlCursor, &match)) {
            if (match.capture_count > 0) {
                TSNode node = match.captures[0].node;
                metaBlocksNodes.emplace_back(node);
            }
        }
    }

    return metaBlocksNodes;
}



// Inline queries - easier+faster than reading from file
// - - - - - - - - - - - - - 

const std::string Highlighter::woowooHighlightQueries = R"(
; Include statement

(include) @keyword
(filename) @string


; Document part

;(document_part "." @operator)
;(document_part_type) @namespace

; Let client do the title, use LS just to highlight environments in title
;(document_part_title) @variable


; Object
;(object ["." ":"] @operator)
;(object_type) @storage.type.struct


; Block

;  - Short Inner Environment

;(short_inner_environment ["." ":"] @operator)
;(short_inner_environment_type) @type
;(short_inner_environment_body) @parameter

;  - Verbose Inner Environment

;(verbose_inner_environment (_ "\"" @string))
;(verbose_inner_environment (_ ["." "@" "#"] @operator))
;(verbose_inner_environment_type) @method
;(verbose_inner_environment_at_end) @method
;(verbose_inner_environment_meta) @modifier

;  - Outer Environment

;(outer_environment_type) @variable.other
;(fragile_outer_environment ["!" ":"] @operator)
;(classic_outer_environment ["." ":"] @operator)

;  - Math

;(math_environment "$" @function)
;(math_environment_body ) @number
)";



const std::string Highlighter::yamlHighlightQueries = R"(
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
)";


