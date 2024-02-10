//
// Created by Michal Janecek on 31.01.2024.
//

#ifndef WUFF_NAVIGATOR_H
#define WUFF_NAVIGATOR_H

#include <string>
#include "../WooWooAnalyzer.h"
#include "../lsp/LSPTypes.h"


class Navigator {

public:
    Navigator(WooWooAnalyzer * analyzer);

    Location goToDefinition(const DefinitionParams & params);

private:
    WooWooAnalyzer * analyzer;

    void prepareQueries();
    static const std::string goToDefinitionQueryString;
    TSQuery * goToDefinitionQuery;

    Location navigateToFile(const DefinitionParams &params, const std::string & relativeFilePath);
    Location resolveShortInnerEnvironmentReference(const DefinitionParams &params, TSNode node);

    Location findReference(const DefinitionParams &params, std::vector<Reference> possibleReferences, std::string referencingValue);
    
    

};


#endif //WUFF_NAVIGATOR_H
