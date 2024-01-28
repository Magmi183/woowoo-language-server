//
// Created by Michal Janecek on 27.01.2024.
//

#include "Shorthand.h"

Shorthand::Shorthand(const std::string& type, const std::string& description, const std::vector<Reference>& references, const MetaBlock& metaBlock)
        : type(type), description(description), references(references), metaBlock(metaBlock) {
}


void Shorthand::deserialize(const YAML::Node& node) {
    if (!node["description"]) {
        throw std::runtime_error("Shorthand YAML node is missing a 'description'");
    }

    description = node["description"].as<std::string>();

    // Deserialize References
    if (node["references"]) {
        references.clear();  // Clear existing references before deserializing
        for (const auto& refNode : node["references"]) {
            Reference ref;
            ref.deserialize(refNode); 
            references.push_back(ref);
        }
    }

    if (node["meta_block"]) {
        metaBlock.deserialize(node["meta_block"]);  
    }
}
