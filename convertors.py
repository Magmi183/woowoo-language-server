
from Wuff import (
    WooWooAnalyzer,
    CompletionParams as WuffCompletionParams,
    TextDocumentIdentifier as WuffTextDocumentIdentifier,
    Position as WuffPosition,
    CompletionContext as WuffCompletionContext,
    CompletionTriggerKind as WuffCompletionTriggerKind,
    CompletionItem as WuffCompletionItem,
    InsertTextFormat as WuffInsertTextFormat,
    CompletionItemKind as WuffCompletionItemKind
)

from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    DidOpenTextDocumentParams, DidChangeTextDocumentParams,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    CompletionOptions, INITIALIZED, TEXT_DOCUMENT_DEFINITION, TEXT_DOCUMENT_DID_SAVE,
    DidSaveTextDocumentParams, TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, SemanticTokensParams,
    SemanticTokensLegend, InitializedParams, InitializeParams, INITIALIZE,
    WorkspaceFolder, DefinitionParams, TEXT_DOCUMENT_FOLDING_RANGE, FoldingRangeParams, WORKSPACE_DID_RENAME_FILES,
    RenameFilesParams, WORKSPACE_WILL_RENAME_FILES, TEXT_DOCUMENT_HOVER, TextDocumentPositionParams, MarkupContent,
    MarkupKind, Hover, SemanticTokens, CompletionList, CompletionParams, CompletionItem, CompletionItemKind,
    InsertTextFormat
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
        trigger_character = ls_params.context.trigger_character if hasattr(ls_params.context, 'trigger_character') else None

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


    insert_text_format = InsertTextFormat.PlainText
    if wuff_item.insertTextFormat:

        if wuff_item.insertTextFormat == WuffInsertTextFormat.Snippet:
            insert_text_format = InsertTextFormat.Snippet
        elif wuff_item.insertTextFormat == WuffInsertTextFormat.PlainText:
            insert_text_format = InsertTextFormat.PlainText


    insert_text = wuff_item.insertText if wuff_item.insertText else ''

    return CompletionItem(label=label, kind=kind, insert_text=insert_text, insert_text_format=insert_text_format)
