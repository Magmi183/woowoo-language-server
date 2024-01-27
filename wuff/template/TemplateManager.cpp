//
// Created by Michal Janecek on 27.01.2024.
//

#include "TemplateManager.h"
#include <yaml-cpp/yaml.h>

TemplateManager::TemplateManager(const std::string& templateFilePath) {
    if (!templateFilePath.empty()) {
        loadTemplate(templateFilePath);
    }
}


void TemplateManager::loadTemplate(const std::string& templateFilePath) {
    YAML::Node yamlData = YAML::LoadFile(templateFilePath);
    activeTemplate = std::make_unique<Template>();
    activeTemplate->deserialize(yamlData);
    processTemplate();  // Call processTemplate here or implement as needed
}

void TemplateManager::processTemplate() {
    // Implement the processing logic for your template
    // This could involve setting up environments, validating data, etc.
}