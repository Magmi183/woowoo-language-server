//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_WOOWOOANALYZER_H
#define WUFF_WOOWOOANALYZER_H


#include <filesystem>
#include <string>
#include <unordered_map>
#include "document/WooWooDocument.h"
#include "parser/Parser.h"
#include "template/TemplateManager.h"

class Hoverer;
class Highlighter;


namespace fs = std::filesystem;

class WooWooAnalyzer {
private:
    std::unordered_map<std::string, std::unordered_map<std::string, WooWooDocument*>> projects;
    std::unordered_map<std::string, std::string> docToProject;
    Parser* parser;
    Hoverer* hoverer;
    Highlighter* highlighter;

public:
    WooWooAnalyzer();
    ~WooWooAnalyzer(); 
    void setTemplate(const std::string& templatePath);
    bool loadWorkspace(const std::string& workspaceUri);
    WooWooDocument * getDocument(const std::string& pathToDoc);
    TemplateManager* templateManager;
    
    // LSP-like functionalities
    std::string hover(const std::string& pathToDoc, int line, int character);
    std::vector<int> semanticTokens(const std::string& pathToDoc);

private:
    std::vector<fs::path> findProjectFolders(const fs::path& rootPath);
    void loadDocument(const fs::path& projectPath, const fs::path& documentPath);
};



#endif //WUFF_WOOWOOANALYZER_H
