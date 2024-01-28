//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_TEMPLATEMANAGER_H
#define WUFF_TEMPLATEMANAGER_H


#include <string>
#include <memory>
#include "Template.h"

class TemplateManager {
    
private:
    template<typename T>
    std::string scanForDescriptionByName(const std::vector<std::shared_ptr<T>>& describables, const std::string& name);
    
public:
    std::unique_ptr<Template> activeTemplate;

    TemplateManager(const std::string& templateFilePath = "");

    void loadTemplate(const std::string& templateFilePath);
    void processTemplate(); 
    
    std::string getDescription(const std::string & type, const std::string & name);
    
};



#endif //WUFF_TEMPLATEMANAGER_H
