from wuff import (
    WooWooAnalyzer,
    CompletionParams as WuffCompletionParams,
    TextDocumentIdentifier as WuffTextDocumentIdentifier,
    Position as WuffPosition,
    WorkspaceEdit as WuffWorkspaceEdit,
    TextEdit as WuffTextEdit,
    CompletionContext as WuffCompletionContext,
    CompletionTriggerKind as WuffCompletionTriggerKind,
    CompletionItem as WuffCompletionItem,
    InsertTextFormat as WuffInsertTextFormat,
    CompletionItemKind as WuffCompletionItemKind,
    Diagnostic as WuffDiagnostic,
    DiagnosticSeverity as WuffDiagnosticSeverity,
    FoldingRange as WuffFoldingRange,
    Location as WuffLocation,
    Position as WuffPosition,
    Range as WuffRange
)

from lsprotocol.types import ( CompletionParams, CompletionItem, CompletionItemKind,
    InsertTextFormat, Diagnostic, Range, Position, DiagnosticSeverity, FoldingRange, FoldingRangeKind, Location,
    WorkspaceEdit, TextEdit
)


def completion_params_ls_to_wuff(ls_params: CompletionParams):
    uri = ls_params.text_document.uri
    line = ls_params.position.line
    character = ls_params.position.character

    text_document = WuffTextDocumentIdentifier(uri)
    position = WuffPosition(line, character)

    context = None
    if hasattr(ls_params, 'context') and ls_params.context is not None:
        trigger_kind = ls_params.context.trigger_kind
        trigger_character = ls_params.context.trigger_character if hasattr(ls_params.context,
                                                                           'trigger_character') else None

        if trigger_kind == 1:
            my_trigger_kind = WuffCompletionTriggerKind.Invoked
        elif trigger_kind == 2:
            my_trigger_kind = WuffCompletionTriggerKind.TriggerCharacter
        elif trigger_kind == 3:
            my_trigger_kind = WuffCompletionTriggerKind.TriggerForIncompleteCompletions
        else:
            raise ValueError("Unknown trigger kind")

        context = WuffCompletionContext(my_trigger_kind, trigger_character)

    return WuffCompletionParams(text_document, position, context)


def wuff_completion_item_to_ls(wuff_item: WuffCompletionItem) -> CompletionItem:
    label = wuff_item.label
    kind = CompletionItemKind.Text
    if wuff_item.kind:

        if wuff_item.kind == WuffCompletionItemKind.Snippet:
            kind = CompletionItemKind.Snippet
        elif wuff_item.kind == WuffCompletionItemKind.Text:
            kind = CompletionItemKind.Text
    else:
        return CompletionItem(label=label)

    insert_text_format = InsertTextFormat.PlainText
    if wuff_item.insertTextFormat:

        if wuff_item.insertTextFormat == WuffInsertTextFormat.Snippet:
            insert_text_format = InsertTextFormat.Snippet
        elif wuff_item.insertTextFormat == WuffInsertTextFormat.PlainText:
            insert_text_format = InsertTextFormat.PlainText

    insert_text = wuff_item.insertText if wuff_item.insertText else ''

    return CompletionItem(label=label, kind=kind, insert_text=insert_text, insert_text_format=insert_text_format)


def wuff_diagnostic_to_ls(wuff_diagnostic: WuffDiagnostic) -> Diagnostic:
    # Convert start and end positions
    start_position = Position(line=wuff_diagnostic.range.start.line, character=wuff_diagnostic.range.start.character)
    end_position = Position(line=wuff_diagnostic.range.end.line, character=wuff_diagnostic.range.end.character)
    diagnostic_range = Range(start=start_position, end=end_position)

    severity = None
    if wuff_diagnostic.severity:
        severity_map = {
            WuffDiagnosticSeverity.Error: DiagnosticSeverity.Error,
            WuffDiagnosticSeverity.Warning: DiagnosticSeverity.Warning,
            WuffDiagnosticSeverity.Information: DiagnosticSeverity.Information,
            WuffDiagnosticSeverity.Hint: DiagnosticSeverity.Hint
        }
        severity = severity_map.get(wuff_diagnostic.severity, None)

    # Construct and return the LSP Diagnostic object
    return Diagnostic(
        range=diagnostic_range,
        message=wuff_diagnostic.message,
        severity=severity,
        source=wuff_diagnostic.source
    )


def wuff_workspace_edit_to_ls(wuff_workspace_edit: WuffWorkspaceEdit) -> WorkspaceEdit:
    ls_changes = {}
    changes = wuff_workspace_edit.changes
    for uri, change_list in changes.items():
        ls_change_list = [wuff_text_edit_to_ls(te) for te in change_list]
        ls_changes[uri] = ls_change_list
    return WorkspaceEdit(changes=ls_changes)

def wuff_text_edit_to_ls(wuff_text_edit: WuffTextEdit) -> TextEdit:

    return TextEdit(wuff_range_to_ls(wuff_text_edit.range), wuff_text_edit.new_text)

def wuff_folding_range_to_ls(wuff_folding_range: WuffFoldingRange) -> FoldingRange:
    return FoldingRange(start_line=wuff_folding_range.start_line,
                        start_character=wuff_folding_range.start_character,
                        end_line=wuff_folding_range.end_line,
                        end_character=wuff_folding_range.end_character,
                        kind=FoldingRangeKind(wuff_folding_range.kind))


def wuff_location_to_ls(wuff_location: WuffLocation):
    if wuff_location.uri == "":
        return None

    return Location(
        uri=wuff_location.uri,
        range=wuff_range_to_ls(wuff_location.range)
    )


def wuff_position_to_ls(wuff_position: WuffPosition):
    return Position(line=wuff_position.line,
                    character=wuff_position.character)


def wuff_range_to_ls(wuff_range: WuffRange):
    return Range(start=wuff_position_to_ls(wuff_range.start),
                 end=wuff_position_to_ls(wuff_range.end))
