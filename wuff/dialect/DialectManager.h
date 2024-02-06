//
// Created by Michal Janecek on 27.01.2024.
//

#ifndef WUFF_DIALECTMANAGER_H
#define WUFF_DIALECTMANAGER_H


#include <string>
#include <memory>
#include "Dialect.h"

class DialectManager {
    
private:
    template<typename T>
    std::string scanForDescriptionByName(const std::vector<std::shared_ptr<T>>& describables, const std::string& name);
    
public:
    std::unique_ptr<Dialect> activeDialect;

    DialectManager(const std::string& dialectFilePath = "");

    void loadDialect(const std::string& dialectFilePath);
    void processDialect(); 
    
    std::string getDescription(const std::string & type, const std::string & name);
    
};



#endif //WUFF_DIALECTMANAGER_H
