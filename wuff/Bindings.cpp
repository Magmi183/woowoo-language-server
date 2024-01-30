//
// Created by Michal Janecek on 27.01.2024.
//


#include <pybind11/pybind11.h>
#include "WooWooAnalyzer.h"
#include "document/WooWooDocument.h"

namespace py = pybind11;

PYBIND11_MODULE(Wuff, m) {
    py::class_<WooWooAnalyzer>(m, "WooWooAnalyzer")
            .def(py::init<>())
            .def("set_template", &WooWooAnalyzer::setTemplate)
            .def("load_workspace", &WooWooAnalyzer::loadWorkspace)
            .def("hover", &WooWooAnalyzer::hover)
            .def("semantic_tokens", &WooWooAnalyzer::semanticTokens);
}

