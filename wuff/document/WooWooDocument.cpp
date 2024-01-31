//
// Created by Michal Janecek on 27.01.2024.
//

#include "WooWooDocument.h"
#include <fstream>
#include <sstream>


WooWooDocument::WooWooDocument(fs::path documentPath1, Parser *parser1) {
    documentPath = documentPath1;
    parser = parser1;
    utfMappings = new UTF8toUTF16Mapping();
    updateSource();
}


void WooWooDocument::updateSource() {
    deleteCommentsAndMetas();
    std::ifstream file(documentPath, std::ios::in | std::ios::binary);
    if (file) {
        std::stringstream buffer;
        buffer << file.rdbuf();
        file.close();

        // Convert the file content into a std::string
        source = buffer.str();
        tree = parser->parseWooWoo(source);
        metaBlocks = parser->parseMetas(tree, source);
        utfMappings->buildMappings(source);
        updateComments();

    } else {
        std::cerr << "Could not open file: " << documentPath << std::endl;
    }
}

void WooWooDocument::updateComments() {

    std::istringstream stream(source);
    std::string line;
    int lineIndex = 0;
    while (std::getline(stream, line)) {
        if(!line.empty() && line[0] == '%')
            commentLines.emplace_back(new CommentLine(lineIndex, line.size()));
        lineIndex++;
    }

}

std::string WooWooDocument::substr(uint8_t startByte, uint8_t endByte) {
    return source.substr(startByte, endByte - startByte);
}

std::string WooWooDocument::getNodeText(TSNode node) {
    // function assumes that the node is a part of this document!
    uint32_t start_byte = ts_node_start_byte(node);
    uint32_t end_byte = ts_node_end_byte(node);
    return substr(start_byte, end_byte);
}

void WooWooDocument::deleteCommentsAndMetas() {
    for (MetaContext *metaBlock: metaBlocks) {
        delete metaBlock;
    }
    metaBlocks.clear();

    for (CommentLine *commentLine: commentLines) {
        delete commentLine;
    }

}

WooWooDocument::~WooWooDocument() {
    deleteCommentsAndMetas();
    ts_tree_delete(tree);
    tree = nullptr;
}