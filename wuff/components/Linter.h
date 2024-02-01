//
// Created by Michal Janecek on 01.02.2024.
//

#ifndef WUFF_LINTER_H
#define WUFF_LINTER_H

#include "../WooWooAnalyzer.h"
#include "../lsp/LSPTypes.h"
#include <vector>

class Linter {

public:
    Linter(WooWooAnalyzer *analyzer);
    std::vector<Diagnostic> diagnose(const TextDocumentIdentifier & tdi);

private:
    WooWooAnalyzer *analyzer;
    void diagnoseErrors(WooWooDocument * doc, std::vector<Diagnostic> & d);
    void diagnoseMissingNodes(WooWooDocument * doc, std::vector<Diagnostic> & d);
    void prepareQueries();
    
    TSQuery * errorNodeQuery;

};


#endif //WUFF_LINTER_H
