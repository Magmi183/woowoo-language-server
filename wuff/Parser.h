//
// Created by Michal Janecek on 28.01.2024.
//

#ifndef WUFF_PARSER_H
#define WUFF_PARSER_H

#include <tree_sitter/api.h>
#include <string>
#include <iostream>

class Parser {
public:
    Parser();
    ~Parser();
    TSTree* parse(const std::string& source);

    // Additional methods for interacting with the syntax tree can be declared here

private:
    TSParser* parser;
};



#endif //WUFF_PARSER_H
