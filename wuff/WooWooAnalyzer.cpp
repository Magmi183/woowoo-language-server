//
// Created by Michal Janecek on 27.01.2024.
//

//#include <pybind11/pybind11.h>
#include <filesystem>
#include <string>
#include <iostream>

#include "WooWooDocument.h"
#include "template/TemplateManager.h"

namespace fs = std::filesystem;


class WooWooAnalyzer {

private:
    std::unordered_map<std::string, std::unordered_map<std::string, WooWooDocument*> > projects;
    TemplateManager * templateManager{};

public:

    void setTemplate(const std::string &templatePath) {
        templateManager = new TemplateManager(templatePath);
    }

    bool loadWorkspace(const std::string &workspacePath) {

        fs::path rootPath = workspacePath;

        auto projectFolders = findProjectFolders(rootPath);

        for (const fs::path& projectFolderPath : projectFolders) {
            for (const auto& entry : fs::recursive_directory_iterator(projectFolderPath)) {
                if (entry.is_regular_file() && entry.path().extension() == ".woo") {
                    // Call the loadDocument method with woo_file and project_folder
                    loadDocument(entry.path().string(), projectFolderPath.string());

                }
            }
        }


        return true;
    }

    std::vector<fs::path>  findProjectFolders(const fs::path &rootPath) {
        std::vector<fs::path> projectFolders;

        for (const auto &entry: fs::recursive_directory_iterator(rootPath)) {
            if (entry.is_regular_file() && entry.path().filename() == "Woofile") {
                // Found a Woofile, add its parent directory to projectFolders
                projectFolders.push_back(entry.path().parent_path());
            }
        }

        return projectFolders;
    }

    void loadDocument(fs::path projectPath, fs::path documentPath){
        projects[projectPath.string()][documentPath.string()] = new WooWooDocument();
    }


};

/*
namespace py = pybind11;

PYBIND11_MODULE(Wuff, m) {
py::class_<WooWooAnalyzer>(m, "WooWooAnalyzer")
.def(py::init<>())
.def("set_template", &WooWooAnalyzer::setTemplate)
.def("load_workspace", &WooWooAnalyzer::loadWorkspace);
}*/