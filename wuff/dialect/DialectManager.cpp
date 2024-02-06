//
// Created by Michal Janecek on 27.01.2024.
//

#include "DialectManager.h"
#include <yaml-cpp/yaml.h>

DialectManager::DialectManager(const std::string& dialectFilePath) {
    if (!dialectFilePath.empty()) {
        loadDialect(dialectFilePath);
    }
}


void DialectManager::loadDialect(const std::string& dialectFilePath) {
    YAML::Node yamlData = YAML::LoadFile(dialectFilePath);
    activeDialect = std::make_unique<Dialect>();
    activeDialect->deserialize(yamlData);
    processDialect();  
}

void DialectManager::processDialect() {
    
}

std::string DialectManager::getDescription(const std::string& type, const std::string& name) {
    std::string description;

    if (type == "outer_environment_type") {
        description = scanForDescriptionByName(activeDialect->classic_outer_environments, name);
        if (description.empty()) {
            description = scanForDescriptionByName(activeDialect->fragile_outer_environments, name);
        }
    } else if (type == "short_inner_environment_type" || type == "verbose_inner_environment_type") {
        description = scanForDescriptionByName(activeDialect->inner_environments, name);
    } else if (type == "document_part_type") {
        description = scanForDescriptionByName(activeDialect->document_parts, name);
    } else if (type == "object_type") {
        description = scanForDescriptionByName(activeDialect->wobjects, name);
    }

    return description; // Return the description if found, or an empty string if not
}
template<typename T>
std::string DialectManager::scanForDescriptionByName(const std::vector<std::shared_ptr<T>>& describables, const std::string& name) {
    static_assert(std::is_base_of<IDescribable, T>::value, "T must derive from IDescribable");

    for (const auto& describable : describables) {
        if (describable->getName() == name) {
            return describable->getDescription();
        }
    }
    return ""; // Return an empty string if no matching describable is found
}