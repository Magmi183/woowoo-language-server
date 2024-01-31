//
// Created by Michal Janecek on 30.01.2024.
//

#ifndef WUFF_HIGHLIGHTER_H
#define WUFF_HIGHLIGHTER_H

#include <string>
#include <vector>

#include "../WooWooAnalyzer.h"

struct NodeInfo {
    TSPoint startPoint;
    TSPoint endPoint;  
    std::string name;  

    NodeInfo(const TSPoint& start, const TSPoint& end, const std::string& captureName)
            : startPoint(start), endPoint(end), name(captureName) {}
};

struct pairHash {
    template <class T1, class T2>
    std::size_t operator () (const std::pair<T1,T2> &pair) const {
        auto hash1 = std::hash<T1>{}(pair.first);
        auto hash2 = std::hash<T2>{}(pair.second);
        return hash1 ^ (hash2 << 1);
    }
};


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
    
    std::unordered_map<std::string, size_t> tokenTypeIndices;
    std::unordered_map<std::string, size_t> tokenModifierIndices;
    void initializeMaps();
    
    void addMetaBlocksNodes(WooWooDocument * document,  std::vector<NodeInfo> & nodes);
    void addCommentNodes(WooWooDocument * document,  std::vector<NodeInfo> & nodes);
};


#endif //WUFF_HIGHLIGHTER_H
