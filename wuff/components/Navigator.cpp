//
// Created by Michal Janecek on 31.01.2024.
//

#include "Navigator.h"
#include "../utils/utils.h"

Navigator::Navigator(WooWooAnalyzer *analyzer) : analyzer(analyzer) {
    
}

Location Navigator::goToDefinition(DefinitionParams params) {

    auto docPath = utils::uriToPathString(params.textDocument.uri);
    // TODO: Finish this after completer is finished.
    return Location();
}
