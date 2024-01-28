//
// Created by Michal Janecek on 28.01.2024.
//

#include "Hoverer.h"

std::string Hoverer::hover(const std::string &docPath, int line, int character) {
    WooWooDocument * document = analyzer->getDocument(docPath);
    
    return  "TODO";
}

Hoverer::Hoverer(WooWooAnalyzer* anal) : analyzer(anal) {}