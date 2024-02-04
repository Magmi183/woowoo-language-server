cmake_minimum_required(VERSION 3.10)
project(Wuff)
set(CMAKE_CXX_STANDARD 20)

# - - - YAML-CPP
include(FetchContent)

FetchContent_Declare(
        yaml-cpp
        GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
        GIT_TAG master # Can be a tag (yaml-cpp-x.x.x), a commit hash, or a branch name (master)
)
FetchContent_GetProperties(yaml-cpp)

if(NOT yaml-cpp_POPULATED)
    message(STATUS "Fetching yaml-cpp...")
    FetchContent_Populate(yaml-cpp)
    add_subdirectory(${yaml-cpp_SOURCE_DIR} ${yaml-cpp_BINARY_DIR})
endif()

# - - - Tree-sitter
FetchContent_Declare(
        tree_sitter
        GIT_REPOSITORY https://github.com/tree-sitter/tree-sitter.git
        GIT_TAG master
)
FetchContent_GetProperties(tree_sitter)

if(NOT tree_sitter_POPULATED)
    message(STATUS "Fetching tree-sitter...")
    FetchContent_Populate(tree_sitter)
    # Since Tree-sitter does not use CMake, we manually add its source and include directories
    set(TREE_SITTER_SRC ${tree_sitter_SOURCE_DIR}/lib/src/lib.c)
    set(TREE_SITTER_INCLUDE_DIRS ${tree_sitter_SOURCE_DIR}/lib/include ${tree_sitter_SOURCE_DIR}/lib/src)
endif()

# Tree-Sitter WooWoo
set(WOOWOO_PARSER_SRC ${CMAKE_CURRENT_SOURCE_DIR}/../tree-sitter/tree-sitter-woowoo/src/parser.c)
set(WOOWOO_SCANNER_SRC ${CMAKE_CURRENT_SOURCE_DIR}/../tree-sitter/tree-sitter-woowoo/src/scanner.cc)

# Tree-Sitter YAML
set(YAML_PARSER_SRC ${CMAKE_CURRENT_SOURCE_DIR}/../tree-sitter/tree-sitter-yaml/src/parser.c)
set(YAML_SCANNER_SRC ${CMAKE_CURRENT_SOURCE_DIR}/../tree-sitter/tree-sitter-yaml/src/scanner.cc)

# - - - - -

# Set the Python version
find_package(Python3 3.9 EXACT REQUIRED Interpreter Development)

add_subdirectory(external/pybind11)
pybind11_add_module(${PROJECT_NAME}
        ${TREE_SITTER_SRC} # Add Tree-sitter lib.c source
        ${WOOWOO_PARSER_SRC}
        ${WOOWOO_SCANNER_SRC}
        ${YAML_PARSER_SRC}
        ${YAML_SCANNER_SRC}
        Bindings.cpp
        WooWooAnalyzer.cpp
        document/WooWooDocument.cpp
        document/MetaContext.cpp
        document/CommentLine.cpp
        document/UTF8toUTF16Mapping.cpp
        template/TemplateManager.cpp
        template/DocumentPart.cpp
        template/Template.cpp
        template/MetaBlock.cpp
        template/Field.cpp
        template/Shorthand.cpp
        template/Reference.cpp
        template/InnerEnvironment.cpp
        template/OuterEnvironment.cpp
        template/Wobject.cpp
        components/Hoverer.cpp
        components/Highlighter.cpp
        components/Navigator.cpp
        components/Completer.cpp
        components/Linter.cpp
        components/Folder.cpp
        parser/Parser.cpp
        utils/utils.cpp
)
target_include_directories(${PROJECT_NAME} PRIVATE ${TREE_SITTER_INCLUDE_DIRS}) # Include Tree-sitter headers
target_link_libraries(${PROJECT_NAME} PUBLIC yaml-cpp::yaml-cpp)

target_compile_definitions(${PROJECT_NAME} PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})

# - - - WooWooTest
add_executable(WooWooTest
        ${TREE_SITTER_SRC}
        ${WOOWOO_PARSER_SRC}
        ${WOOWOO_SCANNER_SRC}
        ${YAML_PARSER_SRC}
        ${YAML_SCANNER_SRC}
        main.cpp
        WooWooAnalyzer.cpp
        document/WooWooDocument.cpp
        document/MetaContext.cpp
        document/CommentLine.cpp
        document/UTF8toUTF16Mapping.cpp
        template/TemplateManager.cpp
        template/DocumentPart.cpp
        template/Template.cpp
        template/MetaBlock.cpp
        template/Field.cpp
        template/Shorthand.cpp
        template/Reference.cpp
        template/InnerEnvironment.cpp
        template/OuterEnvironment.cpp
        template/Wobject.cpp
        components/Hoverer.cpp
        components/Highlighter.cpp
        components/Navigator.cpp
        components/Completer.cpp
        components/Linter.cpp
        components/Folder.cpp
        parser/Parser.cpp
        utils/utils.cpp
)
target_include_directories(WooWooTest PRIVATE ${TREE_SITTER_INCLUDE_DIRS})
target_link_libraries(WooWooTest PUBLIC yaml-cpp::yaml-cpp pybind11::embed)