//
// Created by Michal Janecek on 27.01.2024.
//

#include "WooWooDocument.h"
#include <fstream>  
#include <sstream>


WooWooDocument::WooWooDocument(fs::path documentPath1, Parser *parser1) {
    documentPath = documentPath1;
    parser = parser1;
    updateSource();
}



void WooWooDocument::updateSource() {
    std::ifstream file(documentPath, std::ios::in | std::ios::binary);
    if (file) {
        std::stringstream buffer;
        buffer << file.rdbuf();
        file.close();

        // Convert the file content into a std::string
        source = buffer.str();

        tree = parser->parse(source);
    } else {
        std::cerr << "Could not open file: " << documentPath << std::endl;
    }
}
