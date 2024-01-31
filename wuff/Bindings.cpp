//
// Created by Michal Janecek on 27.01.2024.
//


#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "WooWooAnalyzer.h"
#include "lsp/LSPTypes.h"

namespace py = pybind11;

PYBIND11_MODULE(Wuff, m) {
    py::class_<WooWooAnalyzer>(m, "WooWooAnalyzer")
            .def(py::init<>())
            .def("set_template", &WooWooAnalyzer::setTemplate)
            .def("load_workspace", &WooWooAnalyzer::loadWorkspace)
            .def("hover", &WooWooAnalyzer::hover)
            .def("semantic_tokens", &WooWooAnalyzer::semanticTokens);

    py::class_<Position>(m, "Position")
            .def(py::init<int, int>())
            .def_readwrite("line", &Position::line)
            .def_readwrite("character", &Position::character);

    py::class_<Range>(m, "Range")
            .def(py::init<Position, Position>())
            .def_readwrite("start", &Range::start)
            .def_readwrite("end", &Range::end);

    py::class_<Location>(m, "Location")
            .def(py::init<std::string, Range>())
            .def_readwrite("uri", &Location::uri)
            .def_readwrite("range", &Location::range);

    py::class_<DefinitionParams>(m, "DefinitionParams")
            .def(py::init<TextDocumentIdentifier, Position>())
            .def_readwrite("textDocument", &DefinitionParams::textDocument)
            .def_readwrite("position", &DefinitionParams::position);
}

