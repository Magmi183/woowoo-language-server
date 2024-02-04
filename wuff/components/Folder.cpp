//
// Created by Michal Janecek on 04.02.2024.
//

#include "Folder.h"
#include "../utils/utils.h"

// TODO feat: Add other kinds of folding ranges.

Folder::Folder(WooWooAnalyzer *analyzer) : analyzer(analyzer) {
    prepareQueries();
}

Folder::~Folder() {
    ts_query_delete(foldableTypesQuery);
}

void Folder::prepareQueries() {
    uint32_t errorOffset;
    TSQueryError errorType;
    foldableTypesQuery = ts_query_new(
            tree_sitter_woowoo(),
            foldableTypesQueryString.c_str(),
            foldableTypesQueryString.length(),
            &errorOffset,
            &errorType
    );
}

std::vector<FoldingRange> Folder::foldingRanges(const TextDocumentIdentifier &tdi) {

    auto docPath = utils::uriToPath(tdi.uri);
    auto document = analyzer->getDocument(docPath);
    
    std::vector<FoldingRange> ranges;
    
    TSQueryCursor *cursor = ts_query_cursor_new();
    ts_query_cursor_exec(cursor, foldableTypesQuery, ts_tree_root_node(document->tree));

    TSQueryMatch match;
    while (ts_query_cursor_next_match(cursor, &match)) {
        for (uint32_t i = 0; i < match.capture_count; ++i) {
            TSNode capturedNode = match.captures[i].node;

            TSPoint start_point = ts_node_start_point(capturedNode);
            TSPoint end_point = ts_node_end_point(capturedNode);
            
            FoldingRange fr = FoldingRange(start_point.row, start_point.column, end_point.row, end_point.column, "region");
            ranges.emplace_back(fr);
        }
    }
    ts_query_cursor_delete(cursor);
    
    return ranges;
}


const std::string Folder::foldableTypesQueryString = R"(
(document_part) @dp
(object) @ob
(block) @b
)";