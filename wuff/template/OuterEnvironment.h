//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef OUTERENVIRONMENT_H
#define OUTERENVIRONMENT_H

#include <string>
#include "MetaBlock.h"  // Ensure you have a MetaBlock class defined
#include <yaml-cpp/yaml.h>

class OuterEnvironment {
public:
    std::string name;
    std::string description;
    MetaBlock metaBlock;

    OuterEnvironment() = default;
    OuterEnvironment(const std::string& name, const std::string& description, const MetaBlock& metaBlock = MetaBlock());
    void deserialize(const YAML::Node& node);

};

#endif // OUTERENVIRONMENT_H
