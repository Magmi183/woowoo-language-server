//
// Created by Michal Janecek on 27.01.2024.
//


#include <pybind11/pybind11.h>
#include "WooWooAnalyzer.cpp"
#include "WooWooDocument.h"
// Include other headers as needed

namespace py = pybind11;

PYBIND11_MODULE(Wuff, m) {
    py::class_<WooWooAnalyzer>(m, "WooWooAnalyzer")
            .def(py::init<>())
            .def("set_template", &WooWooAnalyzer::setTemplate)
            .def("load_workspace", &WooWooAnalyzer::loadWorkspace);

    // Add bindings for WooWooDocument and other classes/functions
}

// Repeat for other classes and functions as necessary
