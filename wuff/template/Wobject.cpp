//
// Created by Michal Janecek on 27.01.2024.
//
#include "Wobject.h"

Wobject::Wobject(const std::string& name, const std::string& description, const MetaBlock& metaBlock)
        : name(name), description(description), metaBlock(metaBlock) {
}

void Wobject::deserialize(const YAML::Node& node) {
    if (!node["name"] || !node["description"]) {
        throw std::runtime_error("Wobject YAML node is missing 'name' or 'description'");
    }

    name = node["name"].as<std::string>();
    description = node["description"].as<std::string>();

    if (node["meta_block"]) {
        metaBlock.deserialize(node["meta_block"]);
    }
}