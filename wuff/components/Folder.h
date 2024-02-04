//
// Created by Michal Janecek on 04.02.2024.
//

#ifndef WUFF_FOLDER_H
#define WUFF_FOLDER_H

#include "../WooWooAnalyzer.h"

class Folder {

public:

    Folder(WooWooAnalyzer * analyzer);
    ~Folder();
    
    std::vector<FoldingRange> foldingRanges (const TextDocumentIdentifier & tdi);
    
private:
    
    WooWooAnalyzer * analyzer;
    
    void prepareQueries();
    static const std::string foldableTypesQueryString;
    TSQuery * foldableTypesQuery;

};


#endif //WUFF_FOLDER_H
