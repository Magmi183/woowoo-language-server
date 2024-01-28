//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef DOCUMENTPART_H
#define DOCUMENTPART_H

#include <string>
#include "MetaBlock.h" 
#include <yaml-cpp/yaml.h>

class DocumentPart {
public:
    std::string name;
    std::string description;
    MetaBlock metaBlock;

    DocumentPart() = default;
    DocumentPart(const std::string& name, const std::string& description, const MetaBlock& metaBlock = MetaBlock());
    void deserialize(const YAML::Node& node);


};

#endif // DOCUMENTPART_H
