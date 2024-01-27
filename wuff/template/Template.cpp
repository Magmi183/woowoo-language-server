//
// Created by Michal Janecek on 27.01.2024.
//

#include "Template.h"

void Template::deserialize(const YAML::Node& node) {
    if (!node["name"] || !node["version_code"] || !node["version_name"] || !node["description"] || !node["implicit_outer_environment"]) {
        throw std::runtime_error("Template YAML node is missing one or more required fields.");
    }

    name = node["name"].as<std::string>();
    version_code = node["version_code"].as<std::string>();
    version_name = node["version_name"].as<std::string>();
    description = node["description"].as<std::string>();
    implicit_outer_environment = node["implicit_outer_environment"].as<std::string>();

    // Deserialize DocumentParts
    if (node["document_parts"]) {
        for (const auto& dpNode : node["document_parts"]) {
            auto dp = std::make_unique<DocumentPart>();
            dp->deserialize(dpNode);
            document_parts.push_back(std::move(dp));
        }
    }

    // Deserialize Wobjects
    if (node["wobjects"]) {
        for (const auto& woNode : node["wobjects"]) {
            auto wo = std::make_unique<Wobject>();
            wo->deserialize(woNode);
            wobjects.push_back(std::move(wo));
        }
    }

    // Deserialize Classic Outer Environments
    if (node["classic_outer_environments"]) {
        for (const auto& oeNode : node["classic_outer_environments"]) {
            auto oe = std::make_unique<OuterEnvironment>();
            oe->deserialize(oeNode);
            classic_outer_environments.push_back(std::move(oe));
        }
    }

    // Deserialize Fragile Outer Environments
    if (node["fragile_outer_environments"]) {
        for (const auto& oeNode : node["fragile_outer_environments"]) {
            auto oe = std::make_unique<OuterEnvironment>();
            oe->deserialize(oeNode);
            fragile_outer_environments.push_back(std::move(oe));
        }
    }

    // Deserialize Inner Environments
    if (node["inner_environments"]) {
        for (const auto& ieNode : node["inner_environments"]) {
            auto ie = std::make_unique<InnerEnvironment>();
            ie->deserialize(ieNode);
            inner_environments.push_back(std::move(ie));
        }
    }

    // Deserialize Shorthands
    if (node["shorthands"]["hash"]) {
        shorthand_hash = std::make_unique<Shorthand>();
        shorthand_hash->deserialize(node["shorthands"]["hash"]);
    }

    if (node["shorthands"]["at"]) {
        shorthand_at = std::make_unique<Shorthand>();
        shorthand_at->deserialize(node["shorthands"]["at"]);
    }
}