//
// Created by Michal Janecek on 30.01.2024.
//

#ifndef WUFF_COMMENTLINE_H
#define WUFF_COMMENTLINE_H

class CommentLine {
public:
    CommentLine(int lineNumber, int lineLength)
            : lineNumber(lineNumber), lineLength(lineLength) {}

    int lineNumber;
    int lineLength;
};


#endif //WUFF_COMMENTLINE_H
