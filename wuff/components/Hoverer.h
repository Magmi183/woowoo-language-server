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
    Hoverer(WooWooAnalyzer* anal);

    std::string hover(const std::string& documentUri, int line, int character);

private:
    WooWooAnalyzer * analyzer;
    std::vector<std::string> hoverableNodes = {
            "document_part_type",
            "object_type",
            "short_inner_environment_type",
            "verbose_inner_environment_type",
            "outer_environment_type"
    };

    std::string getHoverText(const std::string& nodeType, const std::string& nodeText);
};

#endif //WUFF_HOVERER_H
