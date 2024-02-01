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

    Location goToDefinition(DefinitionParams);

private:
    WooWooAnalyzer * analyzer;
    

};


#endif //WUFF_NAVIGATOR_H
