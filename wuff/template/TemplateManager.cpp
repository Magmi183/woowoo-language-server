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
    processTemplate();  
}

void TemplateManager::processTemplate() {
    
}

std::string TemplateManager::getDescription(const std::string& type, const std::string& name) {
    std::string description;

    if (type == "outer_environment_type") {
        description = scanForDescriptionByName(activeTemplate->classic_outer_environments, name);
        if (description.empty()) {
            description = scanForDescriptionByName(activeTemplate->fragile_outer_environments, name);
        }
    } else if (type == "short_inner_environment_type" || type == "verbose_inner_environment_type") {
        description = scanForDescriptionByName(activeTemplate->inner_environments, name);
    } else if (type == "document_part_type") {
        description = scanForDescriptionByName(activeTemplate->document_parts, name);
    } else if (type == "object_type") {
        description = scanForDescriptionByName(activeTemplate->wobjects, name);
    }

    return description; // Return the description if found, or an empty string if not
}
template<typename T>
std::string TemplateManager::scanForDescriptionByName(const std::vector<std::shared_ptr<T>>& describables, const std::string& name) {
    static_assert(std::is_base_of<IDescribable, T>::value, "T must derive from IDescribable");

    for (const auto& describable : describables) {
        if (describable->getName() == name) {
            return describable->getDescription();
        }
    }
    return ""; // Return an empty string if no matching describable is found
}