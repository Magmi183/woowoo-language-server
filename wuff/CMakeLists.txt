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

# - - - - -

# Set the Python version
find_package(Python3 3.9 EXACT REQUIRED Interpreter Development)

add_subdirectory(external/pybind11)
pybind11_add_module(${PROJECT_NAME}
        Bindings.cpp
        WooWooAnalyzer.cpp
        WooWooDocument.cpp
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
)
target_link_libraries(${PROJECT_NAME} PUBLIC yaml-cpp::yaml-cpp) # The library or executable that require yaml-cpp library

target_compile_definitions(${PROJECT_NAME} PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})

# - - - WooWooTest
add_executable(WooWooTest main.cpp
        WooWooAnalyzer.cpp
        WooWooDocument.cpp
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
)
target_link_libraries(WooWooTest PUBLIC yaml-cpp::yaml-cpp pybind11::embed)