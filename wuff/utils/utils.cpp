//
// Created by Michal Janecek on 31.01.2024.
//

#include <string>
#include <sstream>
#include <tree_sitter/api.h>

#include "../document/WooWooDocument.h"


namespace utils {
    std::string percentDecode(const std::string &encoded) {
        std::ostringstream decoded;
        for (size_t i = 0; i < encoded.length(); ++i) {
            if (encoded[i] == '%' && i + 2 < encoded.length()) {
                std::string hex = encoded.substr(i + 1, 2);
                char decodedChar = static_cast<char>(std::stoi(hex, nullptr, 16));
                decoded << decodedChar;
                i += 2; // Skip the next two characters
            } else {
                decoded << encoded[i];
            }
        }
        return decoded.str();
    }

    std::string uriToPathString(const std::string &uri) {
        // Assuming the URI starts with 'file://'
        if (uri.substr(0, 7) != "file://") {
            throw std::invalid_argument("URI does not start with 'file://'");
        }
        std::string path = uri.substr(7); // Remove 'file://'

#ifdef _WIN32
        // Special handling for Windows paths that start with a drive letter
    if (path.size() > 2 && path[2] == ':') {
        path.erase(0, 1); // Remove the leading '/' if it exists
    }
#endif

        return percentDecode(path);
    }

    std::string pathToUri(const fs::path &documentPath) {
        std::string uri = "file://";

#ifdef _WIN32
        // On Windows, include the drive letter in the host component
        if (!documentPath.root_name().empty()) {
            uri += "/";
            uri += documentPath.root_name().string();
        }
#endif

        // Convert the path to a generic format, which uses '/' as the directory separator
        uri += documentPath.generic_string();

        return uri;
    }


    std::string getChildText(TSNode node, const char *childType, WooWooDocument *doc) {
        uint32_t child_count = ts_node_child_count(node);
        for (uint32_t i = 0; i < child_count; ++i) {
            TSNode child = ts_node_child(node, i);
            if (strcmp(ts_node_type(child), childType) == 0) {
                return doc->getNodeText(child);
            }
        }
        return ""; // Return an empty string if no matching child is found
    }
} // namespace utils
