//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_WOOWOOANALYZER_H
#define WUFF_WOOWOOANALYZER_H


#include <filesystem>
#include <string>
#include <unordered_map>
#include <pybind11/pytypes.h>
#include "document/WooWooDocument.h"
#include "parser/Parser.h"
#include "template/TemplateManager.h"
#include "lsp/LSPTypes.h"

class Hoverer;
class Highlighter;
class Navigator;
class Completer;
class Linter;


namespace fs = std::filesystem;
namespace py = pybind11;

class WooWooAnalyzer {
private:
    std::unordered_map<std::string, std::unordered_map<std::string, WooWooDocument*>> projects;
    std::unordered_map<std::string, std::string> docToProject;
    Parser* parser;
    Hoverer* hoverer;
    Highlighter* highlighter;
    Navigator * navigator;
    Completer * completer;
    Linter * linter;

public:
    WooWooAnalyzer();
    ~WooWooAnalyzer(); 
    void setTemplate(const std::string& templatePath);
    bool loadWorkspace(const std::string& workspaceUri);
    WooWooDocument * getDocumentByUri(const std::string & docUri);
    WooWooDocument * getDocument(const std::string& pathToDoc);
    TemplateManager* templateManager;
    
    std::vector<WooWooDocument *> getDocumentsFromTheSameProject(WooWooDocument * document);
    
    // LSP-like functionalities
    std::string hover(const std::string& docUri, int line, int character);
    std::vector<int> semanticTokens(const std::string& docUri);
    Location goToDefinition(DefinitionParams params);
    std::vector<CompletionItem> complete(const CompletionParams & params);
    std::vector<Diagnostic> diagnose(const TextDocumentIdentifier & tdi); 

    void documentDidChange(const TextDocumentIdentifier & tdi, std::string &source);
    
private:

    std::vector<fs::path> findProjectFolders(const fs::path& rootPath);
    void loadDocument(const fs::path& projectPath, const fs::path& documentPath);
    void handleDocumentChange(const TextDocumentIdentifier & tdi, std::string & source);
};



#endif //WUFF_WOOWOOANALYZER_H
