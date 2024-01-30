//
// Created by Michal Janecek on 28.01.2024.
//

#ifndef WUFF_HOVERER_H
#define WUFF_HOVERER_H

#include <string>
#include <vector>

#include "../WooWooAnalyzer.h"

class Hoverer {
public:
    Hoverer(WooWooAnalyzer* analyzer);

    std::string hover(const std::string& documentPath, uint32_t line, uint32_t character);

private:
    WooWooAnalyzer * analyzer;
    const char* hoverable_nodes_query_string = "(document_part_type) @node"
                               "(object_type) @node"
                               "(short_inner_environment_type) @node"
                               "(verbose_inner_environment_type) @node"
                               "(outer_environment_type) @node";

    

    std::string getHoverText(const std::string& nodeType, const std::string& nodeText);
};

#endif //WUFF_HOVERER_H
