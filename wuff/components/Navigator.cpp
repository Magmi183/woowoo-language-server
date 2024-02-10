//
// Created by Michal Janecek on 31.01.2024.
//

#include "Navigator.h"

#include <pybind11/attr.h>

#include "../utils/utils.h"

Navigator::Navigator(WooWooAnalyzer *analyzer) : analyzer(analyzer) {
    prepareQueries();
}

Location Navigator::goToDefinition(const DefinitionParams &params) {
    auto document = analyzer->getDocumentByUri(params.textDocument.uri);
    auto pos = document->utfMappings->utf16ToUtf8(params.position.line, params.position.character);
    uint32_t line = pos.first;
    uint32_t character = pos.second;

    TSQueryCursor *cursor = ts_query_cursor_new();
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
            if (nodeType == "short_inner_environment") {
                return resolveShortInnerEnvironmentReference(params, node);
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

Location Navigator::navigateToFile(const DefinitionParams &params, const std::string &relativeFilePath) {
    auto document = analyzer->getDocumentByUri(params.textDocument.uri);
    auto fileBegin = Range{Position{0, 0}, Position{0, 0}};
    fs::path filePath = fs::canonical(document->documentPath.parent_path() / relativeFilePath);
    auto fileUri = "file://" + filePath.generic_string();
    return {fileUri, fileBegin};
}


Location Navigator::resolveShortInnerEnvironmentReference(const DefinitionParams &params, TSNode node) {
    auto document = analyzer->getDocumentByUri(params.textDocument.uri);
    auto shortInnerEnvironmentType = utils::getChildText(node, "short_inner_environment_type", document);

    // obtain what can be referenced by this environment
    std::vector<Reference> referenceTargets = document->dialectManager->getPossibleReferencesByTypeName(shortInnerEnvironmentType);

    // obtain the body part of the referencing environment 
    auto value = utils::getChildText(node, "short_inner_environment_body", document);

    return findReference(params, referenceTargets, value);
}


Location Navigator::findReference(const DefinitionParams &params, std::vector<Reference> possibleReferences, std::string referencingValue) {
    auto document = analyzer->getDocumentByUri(params.textDocument.uri);

    for (auto doc : analyzer->getDocumentsFromTheSameProject(document)) {
        std::optional<std::pair<MetaContext *, TSNode>> foundRef = doc->findReferencable(possibleReferences, referencingValue);
        
        if(foundRef.has_value()) {
            MetaContext * mx = foundRef.value().first;
            TSPoint start_point = ts_node_start_point(foundRef.value().second);
            TSPoint end_point = ts_node_end_point(foundRef.value().second);
            auto s = document->utfMappings->utf8ToUtf16(start_point.row + mx->lineOffset, start_point.column);
            auto e = document->utfMappings->utf8ToUtf16(end_point.row + mx->lineOffset, end_point.column);
            
            Range fieldRange = Range{Position{s.first, s.second}, Position{e.first, e.second}};
            return Location(utils::pathToUri(doc->documentPath), fieldRange);
        }
    }
    return Location("", Range{Position{0, 0}, Position{0, 0}});
}


// - - - - - - -

const std::string Navigator::goToDefinitionQueryString = R"(
(filename) @type
(short_inner_environment) @type
(verbose_inner_environment_hash_end) @type
(verbose_inner_environment_at_end) @type
)";
