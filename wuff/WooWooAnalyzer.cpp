//
// Created by Michal Janecek on 27.01.2024.
//

//#include <pybind11/pybind11.h>
#include <filesystem>
#include <string>
#include <utility>

#include "WooWooAnalyzer.h"
#include "template/TemplateManager.h"
#include "document/WooWooDocument.h"

#include "components/Hoverer.h"
#include "components/Highlighter.h"
#include "components/Navigator.h"
#include "components/Completer.h"

#include "utils/utils.h"

WooWooAnalyzer::WooWooAnalyzer() {
    parser = new Parser();
    
    highlighter = new Highlighter(this); 
    hoverer = new Hoverer(this);
    navigator = new Navigator(this);
    completer = new Completer(this);
}

WooWooAnalyzer::~WooWooAnalyzer() {
    delete parser;
    delete hoverer;
    
    for (auto& project : projects) {
        for (auto& docPair : project.second) {
            delete docPair.second;
        }
    }
}

void WooWooAnalyzer::setTemplate(const std::string& templatePath) {
    templateManager = new TemplateManager(templatePath);
}

bool WooWooAnalyzer::loadWorkspace(const std::string& workspaceUri) {
    fs::path rootPath = utils::uriToPath(workspaceUri);
    auto projectFolders = findProjectFolders(rootPath);

    for (const fs::path& projectFolderPath : projectFolders) {
        for (const auto& entry : fs::recursive_directory_iterator(projectFolderPath)) {
            if (entry.is_regular_file() && entry.path().extension() == ".woo") {
                loadDocument(projectFolderPath, entry.path());
            }
        }
    }

    return true;
}

std::vector<fs::path> WooWooAnalyzer::findProjectFolders(const fs::path& rootPath) {
    
    std::vector<fs::path> projectFolders;
    for (const auto& entry : fs::recursive_directory_iterator(rootPath)) {
        if (entry.is_regular_file() && entry.path().filename() == "Woofile") {
            projectFolders.push_back(entry.path().parent_path());
        }
    }
    return projectFolders;
}

void WooWooAnalyzer::loadDocument(const fs::path& projectPath, const fs::path& documentPath) {
    projects[projectPath.string()][documentPath.string()] = new WooWooDocument(documentPath, parser);
    docToProject[documentPath.string()] = projectPath.string();
}



WooWooDocument * WooWooAnalyzer::getDocument(const std::string &pathToDoc) {
    return projects[docToProject[pathToDoc]][pathToDoc];
}

std::vector<WooWooDocument *> WooWooAnalyzer::getDocumentsFromTheSameProject(WooWooDocument *document) {
    std::vector<WooWooDocument *> documents;
    auto project = docToProject[document->documentPath];
    if (projects.find(project) != projects.end()) {
        std::unordered_map<std::string, WooWooDocument*>& pathDocMap = projects[project];

        for (const auto& pair : pathDocMap) {
            documents.emplace_back(pair.second);
        }
    } else {
        std::cerr << "Project with path '" << project << "' not found in projects map." << std::endl;
    }
    return documents;
}

// - LSP-like public interface - - -

std::string WooWooAnalyzer::hover(const std::string& pathToDoc, int line, int character) {
    return hoverer->hover(pathToDoc, line, character);
}

std::vector<int> WooWooAnalyzer::semanticTokens(const std::string &pathToDoc) {
    return highlighter->semanticTokens(pathToDoc);
}

Location WooWooAnalyzer::goToDefinition(DefinitionParams params) {
    return navigator->goToDefinition(std::move(params));
}

std::vector<CompletionItem> WooWooAnalyzer::complete(const CompletionParams & params){
    return completer->complete(params);
}



// - - - - - - - - - - - - - - - - - 