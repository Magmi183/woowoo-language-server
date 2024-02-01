//
// Created by Michal Janecek on 31.01.2024.
//

#ifndef WUFF_COMPLETER_H
#define WUFF_COMPLETER_H

#include "../WooWooAnalyzer.h"
#include "../lsp/LSPTypes.h"

#include <vector>

class Completer {

public:
    Completer(WooWooAnalyzer * analyzer);
    std::vector<CompletionItem> complete(const CompletionParams & params);
    
private:
    WooWooAnalyzer * analyzer;
    void completeInclude(std::vector<CompletionItem> & completionItems, const CompletionParams & params);
    void completeInnerEnvs(std::vector<CompletionItem> & completionItems, const CompletionParams & params);
    void completeShorthand(std::vector<CompletionItem> & completionItems, const CompletionParams & params);

    void prepareQueries();
    static const std::string includeCollisionQueryString;
    TSQuery * includeCollisionQuery;
    //CompletionParams createCompletionParamsFromPyObject(const py::object & params);
};


#endif //WUFF_COMPLETER_H
