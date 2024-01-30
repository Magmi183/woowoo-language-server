//
// Created by Michal Janecek on 28.01.2024.
//

#include "Hoverer.h"
#include "../parser/Parser.h"

std::string Hoverer::hover(const std::string &docPath, uint32_t line, uint32_t character) {
    WooWooDocument * document = analyzer->getDocument(docPath);
    auto pos = document->utfMappings->utf16ToUtf8(line, character);
    line = pos.first;
    character = pos.second;
    
    uint32_t error_offset;
    TSQueryError error_type;
    TSQuery* query = ts_query_new(tree_sitter_woowoo(), hoverable_nodes_query_string, strlen(hoverable_nodes_query_string), &error_offset, &error_type);

    if (!query) {
        // Handle query compilation error
        std::cerr << "Failed to compile query at offset " << error_offset << " with error " << error_type << std::endl;
        return "";
    }

    TSQueryCursor* cursor = ts_query_cursor_new();
    TSPoint start_point = {line, character};
    TSPoint end_point = {line, character + 1};
    ts_query_cursor_set_point_range(cursor, start_point, end_point);
    ts_query_cursor_exec(cursor, query, ts_tree_root_node(document->tree));

    TSQueryMatch match;
    std::string nodeType;
    std::string nodeText;
    if (ts_query_cursor_next_match(cursor, &match)) {
        if (match.capture_count > 0) {
            TSNode node = match.captures[0].node;
            
            
            nodeType = ts_node_type(node);
            nodeText = document->getNodeText(node);
            
        }
    }
    
    
    ts_query_cursor_delete(cursor);
    ts_query_delete(query);

    
    return analyzer->templateManager->getDescription(nodeType, nodeText);
}

Hoverer::Hoverer(WooWooAnalyzer* anal) : analyzer(anal) {}