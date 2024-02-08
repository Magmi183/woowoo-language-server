//
// Created by Michal Janecek on 08.02.2024.
//

#include "DialectedWooWooDocument.h"
#include <algorithm>
#include "../dialect/DialectManager.h"

DialectedWooWooDocument::DialectedWooWooDocument(const fs::path &documentPath1, Parser *parser1,
                                                 DialectManager *dialectManager)
    : WooWooDocument(documentPath1, parser1), dialectManager(dialectManager) {
    prepareQueries();
    index();
}


DialectedWooWooDocument::~DialectedWooWooDocument() {
    // TODO: Delete queries
}

void DialectedWooWooDocument::index() {
    for (const std::string &typeName: dialectManager->getReferencingTypeNames()) {
        for (const Reference &ref: dialectManager->getPossibleReferencesByTypeName(typeName)) {
            for (MetaContext *mx: metaBlocks) {
                if ((ref.structureType.empty() || ref.structureType == mx->parentType) &&
                    (ref.structureName.empty() || ref.structureName == mx->parentName)) {
                    // this metablock is matching the requiremens by the reference

                    TSQueryCursor *wooCursor = ts_query_cursor_new();
                    ts_query_cursor_exec(wooCursor, fieldQueries[ref.metaKey], ts_tree_root_node(mx->tree));

                    TSQueryMatch match;
                    while (ts_query_cursor_next_match(wooCursor, &match)) {
                        TSNode valueNode;
                        bool correctKey = false;
                        for (uint32_t i = 0; i < match.capture_count; ++i) {
                            uint32_t capture_index = match.captures[i].index;
                            TSNode capturedNode = match.captures[i].node;

                            uint32_t valueCaptureName;
                            const char *valueCaptureNameChars = ts_query_capture_name_for_id(
                                fieldQueries[ref.metaKey], capture_index, &valueCaptureName);
                            std::string valueCaptureNameStr(valueCaptureNameChars, valueCaptureName);

                            if (valueCaptureNameStr == "value") {
                                // mark the value node
                                valueNode = capturedNode;
                            } else if (valueCaptureNameStr == "key") {
                                if (getMetaNodeText(mx, capturedNode) == ref.metaKey) {
                                    // the field key is what we want
                                    correctKey = true;
                                } else {
                                    break;
                                }
                            }
                        }
                        if (!correctKey) continue;
                        referencablesByNode[typeName].push_back(std::make_pair(mx, valueNode));
                        
                    }
                    ts_query_cursor_delete(wooCursor);
                }
            }
        }
    }
}


void DialectedWooWooDocument::prepareQueries() {
    // TODO: Remove and make just one query. Predicates are not supported directly by lib c treesitter.
    for (const auto &reference: dialectManager->allReferences) {
        if (fieldQueries.contains(reference.metaKey)) continue;

        std::ostringstream queryStream;
        queryStream << "(block_mapping_pair "
                << "key: (flow_node [(double_quote_scalar) (single_quote_scalar) (plain_scalar)] @key) "
                << "value: (flow_node) @value "
                << "(#eq? @key \"" << reference.metaKey << "\"))";

        std::string queryString = queryStream.str();
        uint32_t errorOffset;
        TSQueryError errorType;
        TSQuery *query = ts_query_new(
            tree_sitter_yaml(),
            queryString.c_str(),
            queryString.size(),
            &errorOffset,
            &errorType
        );
        fieldQueries[reference.metaKey] = query;
    }
}


std::vector<std::pair<MetaContext *, TSNode> > DialectedWooWooDocument::getReferencablesBy(
    const std::string &referencingTypeName) {
    auto refTypes = dialectManager->getReferencingTypeNames();
    if (std::find(refTypes.begin(), refTypes.end(), referencingTypeName) == refTypes.end()) {
        return {};
    }
    return referencablesByNode[referencingTypeName];
}

void DialectedWooWooDocument::updateSource(std::string &source) {
    WooWooDocument::updateSource(source);
    prepareQueries();
    index();
}