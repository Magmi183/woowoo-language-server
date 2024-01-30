//
// Created by Michal Janecek on 30.01.2024.
//

#ifndef WUFF_HIGHLIGHTER_H
#define WUFF_HIGHLIGHTER_H

#include <string>
#include <vector>

#include "../WooWooAnalyzer.h"

class Highlighter {

public:
    Highlighter(WooWooAnalyzer * analyzer);
    
    std::vector<int> semanticTokens(const std::string& documentPath);
    
private:
    WooWooAnalyzer * analyzer;
    static const std::vector<std::string> tokenTypes;
    static const std::vector<std::string> tokenModifiers;
    static const std::string woowooHighlightQueries;
    static const std::string yamlHighlightQueries;

    std::vector<TSNode> getMetaBlocksNodes(WooWooDocument * document);
};


#endif //WUFF_HIGHLIGHTER_H
