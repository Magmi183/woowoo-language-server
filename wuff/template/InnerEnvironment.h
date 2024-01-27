//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_INNERENVIRONMENT_H
#define WUFF_INNERENVIRONMENT_H


#include <string>
#include <vector>
#include "Reference.h"  
#include "MetaBlock.h"  
#include <yaml-cpp/yaml.h>

class InnerEnvironment {
public:
    std::string name;
    std::string description;
    std::vector<Reference> references; 
    MetaBlock metaBlock;
    InnerEnvironment() = default;
    InnerEnvironment(const std::string& name, const std::string& description, const std::vector<Reference>& references = {}, const MetaBlock& metaBlock = MetaBlock());
    void deserialize(const YAML::Node& node);

};


#endif //WUFF_INNERENVIRONMENT_H
