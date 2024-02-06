//
// Created by Michal Janecek on 31.01.2024.
//

#include "Navigator.h"
#include "../utils/utils.h"

Navigator::Navigator(WooWooAnalyzer *analyzer) : analyzer(analyzer) {
    prepareQueries();
}

Location Navigator::goToDefinition(const DefinitionParams &params) {
    auto document = analyzer->getDocumentByUri(params.textDocument.uri);
    auto pos = document->utfMappings->utf16ToUtf8(params.position.line, params.position.character);
    uint32_t line = pos.first;
    uint32_t character = pos.second;
    
    TSQueryCursor* cursor = ts_query_cursor_new();
    TSPoint start_point = {line, character};
    TSPoint end_point = {line, character + 1};
    ts_query_cursor_set_point_range(cursor, start_point, end_point);
    ts_query_cursor_exec(cursor, goToDefinitionQuery, ts_tree_root_node(document->tree));

    TSQueryMatch match;
    std::string nodeType;
    std::string nodeText;
    if (ts_query_cursor_next_match(cursor, &match)) {
        if (match.capture_count > 0) {
            TSNode node = match.captures[0].node;
            
            nodeType = ts_node_type(node);
            nodeText = document->getNodeText(node);

            if (nodeType == "filename") {
                return navigateToFile(params, nodeText);
            }
            
        }
    }
    return Location("", Range{Position{0, 0}, Position{0, 0}});
}

void Navigator::prepareQueries() {
    uint32_t error_offset;
    TSQueryError error_type;
    TSQuery *query = ts_query_new(tree_sitter_woowoo(), goToDefinitionQueryString.c_str(),
                                  goToDefinitionQueryString.size(),
                                  &error_offset, &error_type);
    goToDefinitionQuery = query;
}

Location Navigator::navigateToFile(const DefinitionParams &params, const std::string & relativeFilePath) {
    auto document = analyzer->getDocumentByUri(params.textDocument.uri);
    auto fileBegin = Range{Position{0,0}, Position{0,0}};
    fs::path filePath = fs::canonical(document->documentPath.parent_path() / relativeFilePath);
    auto fileUri = "file://" + filePath.generic_string();
    return {fileUri, fileBegin};
}



// - - - - - - -

const std::string Navigator::goToDefinitionQueryString = R"(
(filename) @type
(short_inner_environment) @type
(verbose_inner_environment_hash_end) @type
(verbose_inner_environment_at_end) @type
)";

