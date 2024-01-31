//
// Created by Michal Janecek on 31.01.2024.
//

#ifndef WUFF_UTILS_H
#define WUFF_UTILS_H

#include <string>

namespace utils {

    std::string percentDecode(const std::string& encoded);
    std::string uriToPath(const std::string& uri);

} // namespace utils


#endif //WUFF_UTILS_H
