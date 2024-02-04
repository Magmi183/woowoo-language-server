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
            .def("semantic_tokens", &WooWooAnalyzer::semanticTokens)
            .def("go_to_definition", &WooWooAnalyzer::goToDefinition)
            .def("complete", &WooWooAnalyzer::complete)
            .def("document_did_change", &WooWooAnalyzer::documentDidChange)
            .def("open_document", &WooWooAnalyzer::openDocument)
            .def("rename_document", &WooWooAnalyzer::renameDocument)
            .def("diagnose", &WooWooAnalyzer::diagnose)
            .def("set_token_types", &WooWooAnalyzer::setTokenTypes)
            .def("set_token_modifiers", &WooWooAnalyzer::setTokenModifiers);


    py::class_<Position>(m, "Position")
            .def(py::init<uint32_t, uint32_t>())
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

    py::enum_<CompletionTriggerKind>(m, "CompletionTriggerKind")
            .value("Invoked", CompletionTriggerKind::Invoked)
            .value("TriggerCharacter", CompletionTriggerKind::TriggerCharacter)
            .value("TriggerForIncompleteCompletions", CompletionTriggerKind::TriggerForIncompleteCompletions)
            .export_values();
    

    py::class_<TextDocumentIdentifier>(m, "TextDocumentIdentifier")
            .def(py::init<const std::string&>())
            .def_readwrite("uri", &TextDocumentIdentifier::uri);


    py::class_<TextDocumentPositionParams>(m, "TextDocumentPositionParams")
            .def(py::init<TextDocumentIdentifier, Position>())
            .def_readwrite("text_document", &TextDocumentPositionParams::textDocument)
            .def_readwrite("position", &TextDocumentPositionParams::position);

    // just for clarity - internally, it is the same as TextDocumentPositionParams
    py::class_<DefinitionParams, TextDocumentPositionParams>(m, "DefinitionParams")
            .def(py::init<TextDocumentIdentifier, Position>());

   

    py::class_<CompletionContext>(m, "CompletionContext")
            .def(py::init<CompletionTriggerKind, std::optional<std::string>>())
            .def_readwrite("trigger_kind", &CompletionContext::triggerKind)
            .def_readwrite("trigger_character", &CompletionContext::triggerCharacter);

    py::class_<CompletionParams, TextDocumentPositionParams>(m, "CompletionParams")
            .def(py::init<const TextDocumentIdentifier&, const Position&, std::optional<CompletionContext>>())
            .def_readwrite("context", &CompletionParams::context);

    py::enum_<CompletionItemKind>(m, "CompletionItemKind")
            .value("Text", CompletionItemKind::Text)
            .value("Snippet", CompletionItemKind::Snippet)
                    // TODO: other possible values
            .export_values();

    py::enum_<InsertTextFormat>(m, "InsertTextFormat")
            .value("PlainText", InsertTextFormat::PlainText)
            .value("Snippet", InsertTextFormat::Snippet)
            .export_values();

    py::class_<CompletionItem>(m, "CompletionItem")
            .def(py::init<std::string, std::optional<CompletionItemKind>,
                         std::optional<InsertTextFormat>, std::optional<std::string>>(),
                 py::arg("label"), py::arg("kind") = std::nullopt,
                 py::arg("insertTextFormat") = std::nullopt, py::arg("insertText") = std::nullopt)
            .def_readwrite("label", &CompletionItem::label)
            .def_readwrite("kind", &CompletionItem::kind)
            .def_readwrite("insertTextFormat", &CompletionItem::insertTextFormat)
            .def_readwrite("insertText", &CompletionItem::insertText);

    py::enum_<DiagnosticSeverity>(m, "DiagnosticSeverity")
            .value("Error", DiagnosticSeverity::Error)
            .value("Warning", DiagnosticSeverity::Warning)
            .value("Information", DiagnosticSeverity::Information)
            .value("Hint", DiagnosticSeverity::Hint)
            .export_values();

    py::class_<Diagnostic>(m, "Diagnostic")
            .def(py::init<Range, std::string, std::string, DiagnosticSeverity>())
            .def_readwrite("range", &Diagnostic::range)
            .def_readwrite("message", &Diagnostic::message)
            .def_readwrite("source", &Diagnostic::source)
            .def_readwrite("severity", &Diagnostic::severity);

}

