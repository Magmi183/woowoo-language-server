//
// Created by Michal Janecek on 27.01.2024.
//

#include "Shorthand.h"

Shorthand::Shorthand(const std::string& type, const std::string& description, const std::vector<Reference>& references, const MetaBlock& metaBlock)
        : type(type), description(description), references(references), metaBlock(metaBlock) {
}


void Shorthand::deserialize(const YAML::Node& node) {
    if (!node["type"] || !node["description"]) {
        throw std::runtime_error("Shorthand YAML node is missing 'type' or 'description'");
    }

    type = node["type"].as<std::string>();
    description = node["description"].as<std::string>();

    // Deserialize References
    if (node["references"]) {
        references.clear();  // Clear existing references before deserializing
        for (const auto& refNode : node["references"]) {
            Reference ref;
            ref.deserialize(refNode);  // Assuming Reference has a deserialize method
            references.push_back(ref);
        }
    }

    // Deserialize MetaBlock
    if (node["meta_block"]) {
        metaBlock.deserialize(node["meta_block"]);  // Assuming MetaBlock has a deserialize method
    }
}