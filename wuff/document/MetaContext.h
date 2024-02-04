//
// Created by Michal Janecek on 30.01.2024.
//

#ifndef WUFF_METACONTEXT_H
#define WUFF_METACONTEXT_H

#include <tree_sitter/api.h>
#include <string>


class MetaContext {
public:
    MetaContext(TSTree* tree, uint32_t lineOffset, const std::string& parentType, const std::string& parentName);

    TSTree* tree;
    uint32_t lineOffset;
    std::string parentType;
    std::string parentName;
};



#endif //WUFF_METACONTEXT_H
