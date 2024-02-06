//
// Created by Michal Janecek on 27.01.2024.
//

#include "DocumentPart.h"

DocumentPart::DocumentPart(const std::string& name, const std::string& description, const MetaBlock& metaBlock)
        : name(name), description(description), metaBlock(metaBlock) {
}

void DocumentPart::deserialize(const YAML::Node& node) {
    if (!node["name"] || !node["description"]) {
        throw std::runtime_error("DocumentPart YAML node is missing 'name' or 'description'");
    }

    name = node["name"].as<std::string>();
    description = node["description"].as<std::string>();

    // Deserialize 'metaBlock' if it exists
    if (node["meta_block"]) {
        metaBlock.deserialize(node["meta_block"]);
    }
}