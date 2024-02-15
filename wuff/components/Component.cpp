//
// Created by Michal Janecek on 14.02.2024.
//

#include "Component.h"

Component::Component(WooWooAnalyzer *analyzer) : analyzer(analyzer) {}

void Component::prepareQueries() {
    uint32_t errorOffset;
    TSQueryError errorType;

    for (const auto &q: getQueryStringByName()) {
        const auto &queryName = q.first;
        const auto &queryLanguage = q.second.first;
        const auto &queryString = q.second.second;

        TSQuery *query = ts_query_new(
                queryLanguage,
                queryString.c_str(),
                queryString.length(),
                &errorOffset,
                &errorType
        );

        if (!query) {
            std::string errorMessage = "Error compiling query '" + queryName + "': ";

            switch (errorType) {
                case TSQueryErrorSyntax:
                    errorMessage += "Syntax error";
                    break;
                case TSQueryErrorNodeType:
                    errorMessage += "Invalid node type";
                    break;
                case TSQueryErrorField:
                    errorMessage += "Invalid field name";
                    break;
                case TSQueryErrorCapture:
                    errorMessage += "Invalid capture name";
                    break;
                default:
                    errorMessage += "Unknown error";
                    break;
            }

            errorMessage += " at offset " + std::to_string(errorOffset) + ".";

            throw std::runtime_error(errorMessage);
        }

        queries[queryName] = query;
    }
}

Component::~Component() {
    for (auto query: queries) {
        ts_query_delete(query.second);
    }
}