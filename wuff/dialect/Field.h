//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_FIELD_H
#define WUFF_FIELD_H


#include <string>
#include <yaml-cpp/yaml.h>

class Field {
public:
    std::string name;

    explicit Field(const std::string& name);
    void deserialize(const YAML::Node& node);
    Field() = default;
};


#endif //WUFF_FIELD_H
