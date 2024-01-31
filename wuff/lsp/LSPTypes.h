//
// Created by Michal Janecek on 31.01.2024.
//

#ifndef WUFF_LSPTYPES_H
#define WUFF_LSPTYPES_H

struct Position {
    int line;
    int character;
};

struct Range {
    Position start;
    Position end;
};

struct Location {
    std::string uri;
    Range range;
};

using TextDocumentIdentifier = std::string;

struct DefinitionParams {
    TextDocumentIdentifier textDocument;
    Position position;

    DefinitionParams(TextDocumentIdentifier textDocument, Position position)
            : textDocument(std::move(textDocument)), position(position) {}
};

#endif //WUFF_LSPTYPES_H
