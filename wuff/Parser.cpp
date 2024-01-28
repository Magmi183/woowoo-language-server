//
// Created by Michal Janecek on 28.01.2024.
//

#include "Parser.h"
#include <iostream>

// Declare the external function to get the Tree-sitter language object for WooWoo
extern "C" TSLanguage* tree_sitter_woowoo();

Parser::Parser() : parser(ts_parser_new()) {
    // Set the language for the parser to WooWoo
    ts_parser_set_language(parser, tree_sitter_woowoo());
}

Parser::~Parser() {
    // Delete the parser
    if (parser != nullptr) {
        ts_parser_delete(parser);
    }
}

TSTree* Parser::parse(const std::string& source) {
    
    // Parse the given source string and return the new syntax tree
    auto tree = ts_parser_parse_string(parser, nullptr, source.c_str(), source.length());
    return tree;
}

