from lsprotocol.types import FileOperationRegistrationOptions, FileOperationFilter, FileOperationPattern

token_types = [
    'namespace',
    'type',
    'class',
    'enum',
    'interface',
    'struct',
    'typeParameter',
    'parameter',
    'variable',
    'variable.other',  # added
    'storage.type.struct',  # added
    'property',
    'enumMember',
    'event',
    'function',
    'method',
    'macro',
    'keyword',
    'modifier',
    'comment',
    'string',
    'number',
    'regexp',
    'operator',
    'decorator',
]
token_modifiers = [
    'declaration',
    'definition',
    'readonly',
    'static',
    'deprecated',
    'abstract',
    'async',
    'modification',
    'documentation',
    'defaultLibrary'
]

trigger_characters = ['.', ':', '#', '@']

# filter which does not filter anything
no_filter = FileOperationRegistrationOptions(
                    filters=[
                        FileOperationFilter(
                            pattern=FileOperationPattern(glob="**/*"),
                        )
                    ]
                )