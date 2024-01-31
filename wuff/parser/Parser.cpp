//
// Created by Michal Janecek on 28.01.2024.
//

#include "Parser.h"
#include <iostream>



Parser::Parser() : WooWooParser(ts_parser_new()), YAMLParser(ts_parser_new()) {
    // Set the language for the parser to WooWoo
    ts_parser_set_language(WooWooParser, tree_sitter_woowoo());
    ts_parser_set_language(YAMLParser, tree_sitter_yaml());
}

Parser::~Parser() {
        ts_parser_delete(WooWooParser);
        ts_parser_delete(YAMLParser);
}



std::vector<MetaContext *> Parser::parseMetas(TSTree *WooWooTree, const std::string& source) {

    std::vector<MetaContext *> metaBlocks;
    
    const char* queryString = "(meta_block) @metablock";
    uint32_t errorOffset;
    TSQueryError errorType;

    TSQuery* query = ts_query_new(tree_sitter_woowoo(), queryString, std::strlen(queryString), &errorOffset, &errorType);

    if (errorType != TSQueryErrorNone) {
        std::cerr << "Failed to compile query at offset " << errorOffset << " with error type " << errorType << std::endl;
        // TODO: handle
    }

    TSQueryCursor* queryCursor = ts_query_cursor_new();
    ts_query_cursor_exec(queryCursor, query, ts_tree_root_node(WooWooTree));

    TSQueryMatch match;
    uint32_t captureIndex;

    while (ts_query_cursor_next_capture(queryCursor, &match, &captureIndex)) {
        // Get the meta block node from the capture
        TSNode metaBlockNode = match.captures[captureIndex].node;
        
        // Get the parent of the meta block node
        TSNode parent = ts_node_parent(metaBlockNode);

        // Retrieve the type of the parent node
        std::string parentType = ts_node_type(parent);
        std::string parentName = extractStructureName(parent, source);
        
        uint32_t startByte = ts_node_start_byte(metaBlockNode);
        uint32_t endByte = ts_node_end_byte(metaBlockNode);
        std::string yamlText = source.substr(startByte, endByte - startByte); 
        
        TSTree * yamlTree = ts_parser_parse_string(YAMLParser, nullptr, yamlText.c_str(), yamlText.length() );
        auto * metaContext = new MetaContext(yamlTree, ts_node_start_point(metaBlockNode).row, parentType, parentName);
        metaBlocks.emplace_back(metaContext);
    }

    // Cleanup
    ts_query_cursor_delete(queryCursor);
    ts_query_delete(query);
    
    return metaBlocks;
}


TSTree* Parser::parseWooWoo(const std::string& source) {
    // Parse the given source string and return the new syntax tree
    auto tree = ts_parser_parse_string(WooWooParser, nullptr, source.c_str(), source.length());
    return tree;
}

TSTree *Parser::parseYaml(const std::string &source) {
    auto tree = ts_parser_parse_string(YAMLParser, nullptr, source.c_str(), source.length());
    return tree;
}

std::string Parser::extractStructureName(const TSNode &node, const std::string &source) {
    std::string nodeType = ts_node_type(node);

    std::string childWithNameType;
    if (nodeType == "document_part") {
        childWithNameType = "document_part_type";
    } else if (nodeType.find("outer_environment") != std::string::npos) {
        childWithNameType = "outer_environment_type";
    } else if (nodeType == "object") {
        childWithNameType = "object_type";
    }

    if (childWithNameType.empty()) {
        return "";
    }

    uint32_t childCount = ts_node_child_count(node);
    for (uint32_t i = 0; i < childCount; ++i) {
        TSNode child = ts_node_child(node, i);
        std::string childType = ts_node_type(child);

        if (childType == childWithNameType) {
            // Extract the text of the child node from the source code
            uint32_t startByte = ts_node_start_byte(child);
            uint32_t endByte = ts_node_end_byte(child);

            std::string childText = source.substr(startByte, endByte - startByte);

            return childText;
        }
    }

    // Return an empty string if no matching child is found
    return "";
}

