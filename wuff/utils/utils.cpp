//
// Created by Michal Janecek on 31.01.2024.
//

#include <string>
#include <sstream>
#include <iomanip>
#include <cctype>

namespace utils {

    std::string percentDecode(const std::string& encoded) {
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

    std::string uriToPathString(const std::string& uri) {
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

} // namespace utils
