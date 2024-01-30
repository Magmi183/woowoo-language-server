//
// Created by Michal Janecek on 30.01.2024.
//

#include "MetaContext.h"


MetaContext::MetaContext(TSTree* tree, uint32_t lineOffset, const std::string& parentType, const std::string& parentName)
        : tree(tree), lineOffset(lineOffset), parentType(parentType), parentName(parentName) // Initializer list
{
}