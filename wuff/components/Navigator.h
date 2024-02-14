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
    TSQuery * metaFieldQuery;

    Location navigateToFile(const DefinitionParams &params, const std::string & relativeFilePath);
    Location resolveShortInnerEnvironmentReference(const DefinitionParams &params, TSNode node);
    Location resolveShorthandReference(const std::string& shorthandType, const DefinitionParams &params, TSNode node);
    Location resolveMetaBlockReference( const DefinitionParams &params, TSNode node);

    Location findReference(const DefinitionParams &params, const std::vector<Reference>& possibleReferences, const std::string& referencingValue);
    
    

};


#endif //WUFF_NAVIGATOR_H
