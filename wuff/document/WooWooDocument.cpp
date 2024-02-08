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
    std::ifstream file(documentPath, std::ios::in);
    if (file) {
        std::stringstream buffer;
        buffer << file.rdbuf();
        file.close();
        std::string source = buffer.str();
        updateSource(source);

    } else {
        std::cerr << "Could not open file: " << documentPath << std::endl;
    }
}


void WooWooDocument::updateSource(std::string &newSource) {
    this->source = std::move(newSource);
    deleteCommentsAndMetas();
    tree = parser->parseWooWoo(source);
    metaBlocks = parser->parseMetas(tree, source);
    utfMappings->buildMappings(source);
    updateComments();

}

void WooWooDocument::updateComments() {

    std::istringstream stream(source);
    std::string line;
    uint32_t lineIndex = 0;
    while (std::getline(stream, line)) {
        if (!line.empty() && line[0] == '%')
            commentLines.emplace_back(new CommentLine(lineIndex, line.size()));
        lineIndex++;
    }

}

std::string WooWooDocument::substr(uint32_t startByte, uint32_t endByte) const {
    return source.substr(startByte, endByte - startByte);
}

std::string WooWooDocument::getNodeText(TSNode node) {
    // function assumes that the node is a part of this document!
    uint32_t start_byte = ts_node_start_byte(node);
    uint32_t end_byte = ts_node_end_byte(node);
    return substr(start_byte, end_byte);
}

std::string WooWooDocument::getMetaNodeText(MetaContext *mx, TSNode node) {
    uint32_t meta_start_byte = ts_node_start_byte(node);
    uint32_t meta_end_byte = ts_node_end_byte(node);
    return substr(meta_start_byte + mx->byteOffset, meta_end_byte + mx->byteOffset);
}


void WooWooDocument::deleteCommentsAndMetas() {
    for (MetaContext *metaBlock: metaBlocks) {
        delete metaBlock;
    }
    metaBlocks.clear();

    for (CommentLine *commentLine: commentLines) {
        delete commentLine;
    }
    commentLines.clear();

}

WooWooDocument::~WooWooDocument() {
    deleteCommentsAndMetas();
    ts_tree_delete(tree);
    tree = nullptr;
}