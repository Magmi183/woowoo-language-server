//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_TEMPLATEMANAGER_H
#define WUFF_TEMPLATEMANAGER_H


#include <string>
#include <memory>
#include "Template.h"

class TemplateManager {
public:
    std::unique_ptr<Template> activeTemplate;

    TemplateManager(const std::string& templateFilePath = "");

    void loadTemplate(const std::string& templateFilePath);
    void processTemplate(); 

};



#endif //WUFF_TEMPLATEMANAGER_H
