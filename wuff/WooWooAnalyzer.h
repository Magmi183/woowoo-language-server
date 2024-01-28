//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_WOOWOOANALYZER_H
#define WUFF_WOOWOOANALYZER_H


#include <filesystem>
#include <string>
#include <unordered_map>
#include "WooWooDocument.h"
#include "Parser.h"
#include "template/TemplateManager.h"

class Hoverer;

namespace fs = std::filesystem;

class WooWooAnalyzer {
private:
    std::unordered_map<std::string, std::unordered_map<std::string, WooWooDocument*>> projects;
    std::unordered_map<std::string, std::string> docToProject;
    TemplateManager* templateManager;
    Parser* parser;
    Hoverer* hoverer;

public:
    WooWooAnalyzer();
    ~WooWooAnalyzer(); // Remember to declare a destructor to manage dynamic memory
    void setTemplate(const std::string& templatePath);
    bool loadWorkspace(const std::string& workspacePath);
    std::string hover(const std::string& pathToDoc, int line, int character);
    WooWooDocument * getDocument(const std::string& pathToDoc);

private:
    std::vector<fs::path> findProjectFolders(const fs::path& rootPath);
    void loadDocument(const fs::path& projectPath, const fs::path& documentPath);
};



#endif //WUFF_WOOWOOANALYZER_H
