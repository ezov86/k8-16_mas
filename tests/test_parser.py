from args.manager import ArgsManager
from issues.manager import IssuesManager
from parsing.ast import Root, Microinst, MacroinstDef, BitMask, MacrosDef
from parsing.ast_to_dict_visitor import AstToDictVisitor
from parsing.errors import UnexpectedEofError, InvalidSyntaxError, LexerError
from parsing.stage import ParsingStage
import helpers


def get_parser_sample_path(path_in_samples_dir: str, is_valid: bool) -> str:
    return helpers.get_test_path('parser', path_in_samples_dir, is_valid)


def parse(path: str):
    ArgsManager.source_file_path = path

    ast = ParsingStage().handle(ArgsManager)
    helpers.reset_lexer()

    return ast


def eof(rule: str, sample_num: int):
    parse(get_parser_sample_path(f'{rule}/{sample_num}', is_valid=False))
    produced_error = IssuesManager.errors[-1]

    assert isinstance(produced_error, UnexpectedEofError)

    IssuesManager.reset()


def invalid_syntax(rule: str, sample_num: int, line: int, token: str):
    parse(get_parser_sample_path(f'{rule}/{sample_num}', is_valid=False))
    produced_error = IssuesManager.errors[-1]

    print(produced_error)

    assert isinstance(produced_error, InvalidSyntaxError)
    assert produced_error.position.line == line
    assert produced_error.p == token

    IssuesManager.reset()


def invalid_lexem(rule: str, sample_num: int, line: int, token: str, error_index: int):
    parse(get_parser_sample_path(f'{rule}/{sample_num}', is_valid=False))
    produced_error = IssuesManager.errors[error_index]

    assert isinstance(produced_error, LexerError)
    assert produced_error.position.line == line
    assert produced_error.token == token

    IssuesManager.reset()


# Invalid samples.
def test_invalid_lexer():
    invalid_lexem('lexer', 0, 2, '%', -1)
    invalid_lexem('lexer', 1, 1, '%a', -2)


def test_invalid_params():
    rule = 'params'

    invalid_syntax(rule, 0, 2, '{')
    invalid_syntax(rule, 1, 3, ')')
    invalid_syntax(rule, 2, 4, ')')
    invalid_syntax(rule, 3, 3, ',')
    invalid_syntax(rule, 4, 10, '{')
    invalid_syntax(rule, 5, 2, '{')


def test_invalid_bit_masks():
    rule = 'bit_masks'

    invalid_syntax(rule, 0, 3, ';')
    invalid_syntax(rule, 1, 4, 'c')
    invalid_syntax(rule, 2, 5, 'c')
    invalid_syntax(rule, 3, 2, '|')
    invalid_syntax(rule, 4, 2, '|')


def test_invalid_microinstruction():
    rule = 'microinstruction'

    invalid_syntax(rule, 0, 4, '}')
    invalid_syntax(rule, 1, 2, ';')
    invalid_syntax(rule, 2, 4, '@')
    invalid_syntax(rule, 3, 3, ';')


def test_invalid_microinstruction_with_label():
    rule = 'microinstruction_with_label'

    invalid_syntax(rule, 0, 2, ';')
    invalid_syntax(rule, 1, 3, ';')
    invalid_syntax(rule, 2, 2, ':')
    invalid_syntax(rule, 3, 3, 'b')


def test_invalid_macroinstruction_def():
    rule = 'macroinstruction_def'

    invalid_syntax(rule, 0, 3, '}')
    invalid_syntax(rule, 1, 2, 'a')
    eof(rule, 2)
    invalid_syntax(rule, 3, 4, '{')
    invalid_syntax(rule, 4, 1, 'a')


def test_invalid_multiline_macros_def():
    rule = 'multiline_macros_def'

    invalid_syntax(rule, 0, 3, '}')
    invalid_syntax(rule, 1, 2, 'a')
    invalid_syntax(rule, 2, 5, '%i')
    invalid_syntax(rule, 3, 4, '{')
    invalid_syntax(rule, 4, 1, 'a')


def test_invalid_inline_macros_def():
    rule = 'inline_macros_def'

    eof(rule, 0)
    invalid_syntax(rule, 1, 1, '|')
    invalid_syntax(rule, 2, 2, 'a')
    invalid_syntax(rule, 3, 1, '@')


def test_invalid_root():
    rule = 'root'

    eof(rule, 0)
    eof(rule, 1)
    invalid_syntax(rule, 2, 5, '%m')


# Valid samples helpers.
def assert_ast(sample_name: str, expected_ast: Root):
    produced_ast = parse(get_parser_sample_path(sample_name, is_valid=True))
    visitor = AstToDictVisitor(tracking=False)

    assert visitor.visit(produced_ast) == visitor.visit(expected_ast)


nop_body = [Microinst([BitMask('!nop', [])])]


# Valid samples.
def test_empty():
    expected_ast = Root([], [])

    assert_ast('empty', expected_ast)


def test_comments():
    expected_ast = Root([], [
        MacroinstDef('i1', [], [
            Microinst([BitMask('a', [])]),
            Microinst([BitMask('c', []), BitMask('d', [])])
        ])
    ])
    assert_ast('comments', expected_ast)


def test_params():
    expected_ast = Root([], [
        MacroinstDef('i1', ['p1'], nop_body),
        MacroinstDef('i2', ['p1', 'p2'], nop_body),
        MacroinstDef('i3', ['p1', 'p2', 'p3'], nop_body)
    ])

    assert_ast('params', expected_ast)


def test_id_with_params():
    expected_ast = Root([], [
        MacroinstDef('i1', [], nop_body),
        MacroinstDef('i2', ['p1'], nop_body),
        MacroinstDef('i3', ['p1', 'p2'], nop_body),
        MacroinstDef('i4', ['p1', 'p2', 'p3'], nop_body)
    ])

    assert_ast('id_with_params', expected_ast)


def test_bit_mask():
    expected_ast = Root([], [
        MacroinstDef('i1', [], [
            Microinst([
                BitMask('a', [])
            ]),
            Microinst([
                BitMask('a', ['1']),
                BitMask('b', [])
            ]),
            Microinst([
                BitMask('a', []),
                BitMask('b', ['2']),
                BitMask('c', [])
            ])
        ]),
    ])

    assert_ast('bit_mask', expected_ast)


def test_microinstruction():
    expected_ast = Root([], [
        MacroinstDef('i1', [], [
            Microinst([
                BitMask('a', [])
            ], next_microinst_label='l1'),
            Microinst([
                BitMask('a', []),
                BitMask('b', []),
                BitMask('c', [])
            ], next_microinst_label='l2'),
            Microinst([
                BitMask('a', [])
            ]),
            Microinst([
                BitMask('b', []),
                BitMask('c', [])
            ])
        ])
    ])

    assert_ast('microinstruction', expected_ast)


def test_microinstruction_with_label():
    expected_ast = Root([], [
        MacroinstDef('i1', [], [
            Microinst([BitMask('a', [])]),
            Microinst([BitMask('b', [])], label='l1'),
            Microinst([BitMask('c', []), BitMask('d', [])]),
            Microinst([BitMask('a', []), BitMask('b', [])], label='l2')
        ]),
    ])

    assert_ast('microinstruction_with_label', expected_ast)


def test_macroinstruction_def():
    expected_ast = Root([], [
        MacroinstDef('i1', [], [
            Microinst([BitMask('a', [])]),
        ]),
        MacroinstDef('i2', ['+', '-'], [
            Microinst([BitMask('a', [])]),
            Microinst([BitMask('b', [])])
        ]),
        MacroinstDef('i3', ['1'], [
            Microinst([BitMask('a', [])]),
            Microinst([BitMask('b', [])]),
            Microinst([BitMask('c', [])])
        ])
    ])

    assert_ast('macroinstruction_def', expected_ast)


def test_multiline_macros_def():
    expected_ast = Root(
        [
            MacrosDef('m1', [], [
                Microinst([BitMask('a', [])]),
            ]),
            MacrosDef('m2', ['*'], [
                Microinst([BitMask('a', [])]),
                Microinst([BitMask('b', [])]),
            ]),
            MacrosDef('m3', ['1', '2'], [
                Microinst([BitMask('a', [])]),
                Microinst([BitMask('b', [])]),
                Microinst([BitMask('c', [])])
            ]),
        ],
        [MacroinstDef('i1', [], nop_body)]
    )

    assert_ast('multiline_macros_def', expected_ast)


def test_inline_macros_def():
    expected_ast = Root(
        [
            MacrosDef('mi1', [], [Microinst([BitMask('a', [])])], is_inline=True),
            MacrosDef('mi2', ['a'], [Microinst([BitMask('a', []), BitMask('b', []), BitMask('c', [])])],
                      is_inline=True)
        ],
        [MacroinstDef('i1', [], nop_body)]
    )

    assert_ast('inline_macros_def', expected_ast)


def test_macros_def():
    expected_ast = Root(
        [
            MacrosDef('m1', [], nop_body),
            MacrosDef('mi1', [], nop_body, is_inline=True),
            MacrosDef('m2', [], nop_body),
            MacrosDef('mi2', [], nop_body, is_inline=True)
        ],
        [MacroinstDef('i1', [], nop_body)]
    )

    assert_ast('macros_def', expected_ast)


def test_root():
    expected_ast = Root(
        [MacrosDef('m1', [], nop_body)],
        [MacroinstDef('i1', [], nop_body)]
    )

    assert_ast('root', expected_ast)
