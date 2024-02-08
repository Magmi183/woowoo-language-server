//
// Created by Michal Janecek on 08.02.2024.
//

#ifndef TEMPLATED_WOOWOO_DOCUMENT_H
#define TEMPLATED_WOOWOO_DOCUMENT_H

#include "WooWooDocument.h"
#include "../dialect/DialectManager.h"
#include <filesystem>
#include "tree_sitter/api.h"

namespace fs = std::filesystem;

class DialectedWooWooDocument : public WooWooDocument {
public:
    
    DialectedWooWooDocument(const fs::path& documentPath1, Parser* parser1, DialectManager * dialectManager);

    
    virtual ~DialectedWooWooDocument();
    std::vector<std::pair<MetaContext *, TSNode>> getReferencablesBy(const std::string& referencingTypeName);
    void updateSource(std::string &source) override;
private:

    DialectManager * dialectManager;

    void prepareQueries();
    void index();
    std::unordered_map<std::string, TSQuery *> fieldQueries;
    std::unordered_map<std::string, std::vector<std::pair<MetaContext *, TSNode>> > referencablesByNode;
};

#endif 
