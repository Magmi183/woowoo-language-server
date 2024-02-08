//
// Created by Michal Janecek on 27.01.2024.
//

#include "DialectManager.h"
#include <yaml-cpp/yaml.h>

DialectManager::DialectManager(const std::string &dialectFilePath) {
    if (!dialectFilePath.empty()) {
        loadDialect(dialectFilePath);
    }
}


void DialectManager::loadDialect(const std::string &dialectFilePath) {
    YAML::Node yamlData = YAML::LoadFile(dialectFilePath);
    activeDialect = std::make_unique<Dialect>();
    activeDialect->deserialize(yamlData);
    processDialect();
}

void DialectManager::processDialect() {
    collectReferences();
}

std::string DialectManager::getDescription(const std::string &type, const std::string &name) {
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
std::string DialectManager::scanForDescriptionByName(const std::vector<std::shared_ptr<T> > &describables,
                                                     const std::string &name) {
    static_assert(std::is_base_of<IDescribable, T>::value, "T must derive from IDescribable");

    for (const auto &describable: describables) {
        if (describable->getName() == name) {
            return describable->getDescription();
        }
    }
    return ""; // Return an empty string if no matching describable is found
}

void DialectManager::collectReferences() {
    for (const std::shared_ptr<InnerEnvironment> &ie: activeDialect->inner_environments) {
        allReferences.insert(allReferences.end(), ie->references.begin(), ie->references.end());
        extractReferences(ie->metaBlock, allReferences);
    }

    for (const std::shared_ptr<OuterEnvironment> &coe: activeDialect->classic_outer_environments) {
        extractReferences(coe->metaBlock, allReferences);
    }

    for (const std::shared_ptr<OuterEnvironment> &foe: activeDialect->fragile_outer_environments) {
        extractReferences(foe->metaBlock, allReferences);
    }

    for (const std::shared_ptr<DocumentPart> &dp: activeDialect->document_parts) {
        extractReferences(dp->metaBlock, allReferences);
    }

    for (const std::shared_ptr<Wobject> &w: activeDialect->wobjects) {
        extractReferences(w->metaBlock, allReferences);
    }

    extractReferences(activeDialect->shorthand_at->metaBlock, allReferences);
    extractReferences(activeDialect->shorthand_hash->metaBlock, allReferences);
}

void DialectManager::extractReferences(const MetaBlock &mb, std::vector<Reference> &target) const {
    for (auto field: mb.optionalFields) {
        target.insert(target.end(), field.references.begin(), field.references.end());
    }
    for (auto field: mb.requiredFields) {
        target.insert(target.end(), field.references.begin(), field.references.end());
    }
}

std::vector<std::string> DialectManager::getReferencingTypeNames() {
    std::vector<std::string> names;

    for (const std::shared_ptr<InnerEnvironment> &ie: activeDialect->inner_environments) {
        if (!ie->references.empty()) {
            names.push_back(ie->name);
        }
    }

    if (!activeDialect->shorthand_at->references.empty()) {
        names.push_back("@");
    }

    if (!activeDialect->shorthand_hash->references.empty()) {
        names.push_back("#");
    }

    // TODO: Also add names of the metablock fields.
    return names;
}

std::vector<Reference> DialectManager::getPossibleReferencesByTypeName(const std::string &name) {
    for (const std::shared_ptr<InnerEnvironment> &ie: activeDialect->inner_environments) {
        if (ie->name == name) {
            return ie->references;
        }
    }

    if (name == "@") {
        return activeDialect->shorthand_at->references;
    }

    if (name == "#") {
        return activeDialect->shorthand_hash->references;
    }


    // TODO: Also add names of the metablock fields.
    return {};
}
