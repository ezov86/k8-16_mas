import os

from issues.manager import IssuesManager
from parsing.ast import Root, Microinstruction, MacroinstructionDefinition, BitMask, MacrosDefinition
from parsing.ast_to_dict_visitor import AstToDictVisitor
from parsing.errors import UnexpectedEofError, InvalidSyntaxError, LexerError
from parsing.lexer import lexer
from parsing.parser import parser

if os.path.isdir('parser_samples'):
    root_dir = '.'  # pragma: no cover
else:
    root_dir = 'tests'  # pragma: no cover


def parse(text: str):
    ast = parser.parse(text, tracking=True)
    lexer.lineno = 1

    return ast


def load_sample(path_in_samples_dir: str) -> str:
    with open(f'{root_dir}/parser_samples/{path_in_samples_dir}.mas', 'r') as file:
        return file.read()


# Invalid samples helpers.
def load_invalid(rule: str, sample_num: int) -> str:
    return load_sample(f'invalid/{rule}/{sample_num}')


def eof(rule: str, sample_num: int):
    parse(load_invalid(rule, sample_num))
    produced_error = IssuesManager().errors[-1]

    assert isinstance(produced_error, UnexpectedEofError)


def invalid_syntax(rule: str, sample_num: int, line: int, token: str):
    parse(load_invalid(rule, sample_num))
    produced_error = IssuesManager().errors[-1]

    print(produced_error)

    assert isinstance(produced_error, InvalidSyntaxError)
    assert str(produced_error) == f'ERROR at line {line}: invalid syntax near "{token}".'


def invalid_lexem(rule: str, sample_num: int, line: int, token: str, error_index: int):
    parse(load_invalid(rule, sample_num))
    produced_error = IssuesManager().errors[error_index]

    assert isinstance(produced_error, LexerError)
    assert str(produced_error) == f'ERROR at line {line}: invalid token "{token}".'


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


def test_invalid_root():
    rule = 'root'

    eof(rule, 0)
    eof(rule, 1)
    invalid_syntax(rule, 2, 5, '%m')


# Valid samples helpers.
def load_valid(sample_name: str) -> str:
    return load_sample(f'valid/{sample_name}')


def assert_ast(sample_name: str, expected_ast: Root):
    produced_ast = parse(load_valid(sample_name))
    visitor = AstToDictVisitor(tracking=False)

    assert visitor.visit(produced_ast) == visitor.visit(expected_ast)


nop_body = [Microinstruction([BitMask('!nop', [])])]


# Valid samples.
def test_empty():
    expected_ast = Root([], [])

    assert_ast('empty', expected_ast)


def test_comments():
    expected_ast = Root([], [
        MacroinstructionDefinition('i1', [], [
            Microinstruction([BitMask('a', [])]),
            Microinstruction([BitMask('c', []), BitMask('d', [])])
        ])
    ])
    assert_ast('comments', expected_ast)


def test_params():
    expected_ast = Root([], [
        MacroinstructionDefinition('i1', ['p1'], nop_body),
        MacroinstructionDefinition('i2', ['p1', 'p2'], nop_body),
        MacroinstructionDefinition('i3', ['p1', 'p2', 'p3'], nop_body)
    ])

    assert_ast('params', expected_ast)


def test_id_with_params():
    expected_ast = Root([], [
        MacroinstructionDefinition('i1', [], nop_body),
        MacroinstructionDefinition('i2', ['p1'], nop_body),
        MacroinstructionDefinition('i3', ['p1', 'p2'], nop_body),
        MacroinstructionDefinition('i4', ['p1', 'p2', 'p3'], nop_body)
    ])

    assert_ast('id_with_params', expected_ast)


def test_bit_mask():
    expected_ast = Root([], [
        MacroinstructionDefinition('i1', [], [
            Microinstruction([
                BitMask('a', [])
            ]),
            Microinstruction([
                BitMask('a', ['1']),
                BitMask('b', [])
            ]),
            Microinstruction([
                BitMask('a', []),
                BitMask('b', ['2']),
                BitMask('c', [])
            ])
        ]),
    ])

    assert_ast('bit_mask', expected_ast)


def test_microinstruction():
    expected_ast = Root([], [
        MacroinstructionDefinition('i1', [], [
            Microinstruction([
                BitMask('a', [])
            ], next_microinstruction_label='l1'),
            Microinstruction([
                BitMask('a', []),
                BitMask('b', []),
                BitMask('c', [])
            ], next_microinstruction_label='l2'),
            Microinstruction([
                BitMask('a', [])
            ]),
            Microinstruction([
                BitMask('b', []),
                BitMask('c', [])
            ])
        ])
    ])

    assert_ast('microinstruction', expected_ast)


def test_microinstruction_with_label():
    expected_ast = Root([], [
        MacroinstructionDefinition('i1', [], [
            Microinstruction([BitMask('a', [])]),
            Microinstruction([BitMask('b', [])], label='l1'),
            Microinstruction([BitMask('c', []), BitMask('d', [])]),
            Microinstruction([BitMask('a', []), BitMask('b', [])], label='l2')
        ]),
    ])

    assert_ast('microinstruction_with_label', expected_ast)


def test_macroinstruction_def():
    expected_ast = Root([], [
        MacroinstructionDefinition('i1', [], [
            Microinstruction([BitMask('a', [])]),
        ]),
        MacroinstructionDefinition('i2', ['+', '-'], [
            Microinstruction([BitMask('a', [])]),
            Microinstruction([BitMask('b', [])])
        ]),
        MacroinstructionDefinition('i3', ['1'], [
            Microinstruction([BitMask('a', [])]),
            Microinstruction([BitMask('b', [])]),
            Microinstruction([BitMask('c', [])])
        ])
    ])

    assert_ast('macroinstruction_def', expected_ast)


def test_multiline_macros_def():
    expected_ast = Root(
        [
            MacrosDefinition('m1', [], [
                Microinstruction([BitMask('a', [])]),
            ]),
            MacrosDefinition('m2', ['*'], [
                Microinstruction([BitMask('a', [])]),
                Microinstruction([BitMask('b', [])]),
            ]),
            MacrosDefinition('m3', ['1', '2'], [
                Microinstruction([BitMask('a', [])]),
                Microinstruction([BitMask('b', [])]),
                Microinstruction([BitMask('c', [])])
            ]),
        ],
        [MacroinstructionDefinition('i1', [], nop_body)]
    )

    assert_ast('multiline_macros_def', expected_ast)


def test_inline_macros_def():
    expected_ast = Root(
        [
            MacrosDefinition('mi1', [], [Microinstruction([BitMask('a', [])])], is_inline=True),
            MacrosDefinition('mi2', ['a'], [Microinstruction([BitMask('a', []), BitMask('b', []), BitMask('c', [])])],
                             is_inline=True)
        ],
        [MacroinstructionDefinition('i1', [], nop_body)]
    )

    assert_ast('inline_macros_def', expected_ast)


def test_macros_def():
    expected_ast = Root(
        [
            MacrosDefinition('m1', [], nop_body),
            MacrosDefinition('mi1', [], nop_body, is_inline=True),
            MacrosDefinition('m2', [], nop_body),
            MacrosDefinition('mi2', [], nop_body, is_inline=True)
        ],
        [MacroinstructionDefinition('i1', [], nop_body)]
    )

    assert_ast('macros_def', expected_ast)


def test_root():
    expected_ast = Root(
        [MacrosDefinition('m1', [], nop_body)],
        [MacroinstructionDefinition('i1', [], nop_body)]
    )

    assert_ast('root', expected_ast)
