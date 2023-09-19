module.exports = grammar({
    name: 'woowoo',
    conflicts: $ => [
        [$.verbose_inner_environment_body],
        [$.document_part_body], // not clear whether multiemptyline separates docpart/blocks
        [$.document_part], // not clear whether multiemptyline separates docpart/blocks (docpart can be empty)
    ],
    externals: $ => [
        $._text_no_space_no_dot, // higher precedence than text!
        $.text,
        $.fragile_outer_environment_body,
        $._comment,
        $.verbose_inner_environment_meta,
        $._ex_indent,
        $._ex_dedent,
        $._ex_newline,
        $._ex_empty_line,
        $._ex_multi_empty_line,
        $.error_sentinel
    ],

    extras: $ => [
        $._comment
    ],

    rules: {

        source_file: $ => seq(
            optional(
                choice($._ex_empty_line, $._ex_multi_empty_line)
            ),
            choice($.include, $.document_part),
            repeat(
                choice(
                    seq(
                        $._ex_multi_empty_line,
                        $.document_part
                    ),
                    seq(
                        choice($._ex_multi_empty_line, $._ex_empty_line),
                        $.include
                    ))
            ),
            optional(
                choice(
                    $._ex_multi_empty_line,
                    $._ex_empty_line,
                    repeat($._newline_char)
                )
            )
        ),

        // the newline is optional, because an include could be the last line of a file
        // precedence in this case means that if there is a newline, it always belongs to this include
        include: $ => prec.left(seq(
            ".include ",
            $.filename,
            optional($._newline_char)
        )),

        filename: $ => /[^\r\n]+/,

        document_part: $ => seq(
            '.',
            $.document_part_type,
            ' ',
            $.document_part_title,
            optional($.meta_block),
            optional($.document_part_body)
        ),

        document_part_type: $ => seq(
            $._uppercase_letter,
            repeat($._document_part_type_char)
        ),

        document_part_title: $ => /[^[\n\r]]+/,

        meta_block: $ => seq(
            $._ex_indent,
            repeat1(
                seq(
                    $._meta_block_content,
                    optional($._ex_newline)
                )
            ),
            $._ex_dedent,
        ),

        _meta_block_content: $ => /[^\n\r]*/,

        /* ORIGINAL (DML STYLE)
        document_part_body: $ =>
            repeat1(
                seq($._ex_multi_empty_line,
                    $._document_part_content
                )
            ),*/

        document_part_body: $ => seq(
            choice($._ex_multi_empty_line, $._ex_empty_line),
            $._document_part_content,
            repeat(
                seq($._ex_multi_empty_line,
                    $._document_part_content
                )
            )),

        _document_part_content: $ => choice($.object, $.block),

        // OBJECT
        // ---------------- >>>>>>>>>>>>

        object: $ => seq(
            '.',
            $.object_type,
            ':',
            choice($._newline_char,
                $.meta_block),
            $._ex_indent,
            $._object_body,
            $._ex_dedent
        ),

        object_type: $ => seq(
            $._uppercase_letter,
            repeat($._letter)
        ),

        _object_body: $ => seq(
            $.block,
            repeat(
                seq(
                    $._ex_multi_empty_line,
                    $.block
                )
            )
        ),

        // <<<<<<<<<<<<<  ----------------


        // BLOCK
        // ---------------- >>>>>>>>>>>>


        block: $ => prec.right(seq(
            choice($._outer_environment, $.text_block),
            repeat(choice(
                    seq($._ex_empty_line,
                        choice($._explicit_outer_environment, $.text_block)
                    ),
                    $.implicit_outer_environment
                )
            )
        )),

        text_block: $ => prec.right(seq(
            $._text_block_line,
            repeat(
                seq($._ex_newline,
                    $._text_block_line
                )
            ),
            optional(choice($.meta_block, $._ex_newline))
        )),

        _text_block_line: $ => repeat1(
            choice(
                $._inner_environment, $.text, $.math_environment
            )
        ),


        // --- ENVIRONMENTS
        // ----------------

        // TODO: Add math_environment tests + fix the issue where $ cant appear in text
        math_environment: $ => seq(
            "$",
            $.math_environment_body,
            "$"
        ),

        math_environment_body: $ => /[^$]*/,

        _inner_environment: $ => choice($.short_inner_environment, $.verbose_inner_environment),

        short_inner_environment: $ => seq(
            '.',
            $.short_inner_environment_type,
            ':',
            $.short_inner_environment_body
        ),

        short_inner_environment_type: $ => seq(
            $._lowercase_letter,
            /[a-zA-Z_-]+/
        ),

        // TODO: Up to debate which chars belong here, for example, does ':' belong? dot is also for debate?
        short_inner_environment_body: $ => /[^ ".\n\r]+/,

        verbose_inner_environment_body: $ => repeat1(
            choice(
                $._inner_environment,
                $.text,
                $.math_environment
            )
        ),

        verbose_inner_environment: $ =>
            choice($.verbose_inner_environment_classic,
                $.verbose_inner_environment_at,
                $.verbose_inner_environment_hashtag),

        verbose_inner_environment_classic: $ => seq(
            '"',
            $.verbose_inner_environment_body,
            '"',
            $._verbose_inner_environment_end
        ),
        verbose_inner_environment_at: $ => seq(
            '"',
            $.verbose_inner_environment_body,
            '"',
            $._verbose_inner_environment_at_end
        ),
        verbose_inner_environment_hashtag: $ => seq(
            '"',
            $.verbose_inner_environment_body,
            '"',
            $._verbose_inner_environment_hashtag_end
        ),

        _verbose_inner_environment_end: $ => prec.right(seq(
            '.',
            $.verbose_inner_environment_type,
            optional($.verbose_inner_environment_meta)
        )),


        _verbose_inner_environment_hashtag_end: $ => seq('#', $.verbose_inner_environment_type),

        _verbose_inner_environment_at_end: $ => seq('@', $.verbose_inner_environment_at_type),

        // TODO: The name of this is up to discussion. It is de facto a meta.
        // Probably wrong, much more characters are unwanted, like ,!? etc.
        verbose_inner_environment_at_type: $ => $._text_no_space_no_dot,

        verbose_inner_environment_type: $ => seq(
            $._lowercase_letter,
            /[a-zA-Z_-]+/
        ),


        // OUTER:

        _outer_environment: $ => choice($.implicit_outer_environment, $._explicit_outer_environment),

        _explicit_outer_environment: $ => choice($.fragile_outer_environment, $.classic_outer_environment),

        fragile_outer_environment: $ => seq(
            '!',
            $.outer_environment_type,
            ':',
            choice($._newline_char,
                $.meta_block),
            $._ex_indent,
            $.fragile_outer_environment_body,
            $._ex_dedent
        ),

        classic_outer_environment: $ => seq(
            '.',
            $.outer_environment_type,
            ':',
            choice($._newline_char,
                $.meta_block),
            $._ex_indent, // the indent "includes" empty line
            $.block,
            $._ex_dedent
        ),

        outer_environment_type: $ => /[a-z]+/, // TODO add more chars? + WARNING: DETECTION IN SCANNER ONLY COUNTS WITH CHARS,
        // IF YOU ALLOW MORE, YOU NEED TO MANUALLY ADJUST SCANNER

        implicit_outer_environment: $ => seq(
            $._ex_indent,
            $.block,
            $._ex_dedent
        ),

        // <<<<<<<<<<<<<  ----------------


        // ----------------

        _letter: $ => /[a-zA-Z]/,
        _uppercase_letter: $ => /[A-Z]/,
        _lowercase_letter: $ => /[a-z]/,

        _newline_char: $ => choice('\n', '\r\n'),

        _space: $ => ' ',


        // ---

        _document_part_type_char: $ => $._letter,

        _inn_env_type_char: $ => /[a-zA-Z_-]/, // letters, underscore and -
    },

});