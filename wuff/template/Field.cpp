//
// Created by Michal Janecek on 27.01.2024.
//

#include "Field.h"

Field::Field(const std::string& name) : name(name) {
}

void Field::deserialize(const YAML::Node& node) {
    if (node["name"]) {
        name = node["name"].as<std::string>();
    } else {
        throw std::runtime_error("Field node does not have a 'name' attribute.");
    }
}