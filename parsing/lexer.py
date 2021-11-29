import ply.lex as lex

from parsing.errors import LexerError

tokens = ('ID', 'PIPE', 'SEMICOLON', 'LPAR', 'RPAR', 'COMMA', 'LBRACE', 'RBRACE', 'MULTILINE_MACROS', 'INLINE_MACROS',
          'MACROINSTRUCTION', 'AT', 'COLON')

t_PIPE = r'\|'
t_SEMICOLON = r'\;'
t_LPAR = r'\('
t_RPAR = r'\)'
t_COMMA = r'\,'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_MULTILINE_MACROS = r'\%m'
t_INLINE_MACROS = r'\%mi'
t_MACROINSTRUCTION = r'\%i'
t_AT = r'@'
t_COLON = r':'


def t_NEWLINE(t):
    r"""\n"""
    t.lexer.lineno += 1


def t_COMMENT(t):
    r"""\#[^\n\r]*"""
    t.lexer.lineno += t.value.count('\n')


def t_ID(t):
    r"""[^\s|;(),%{}@:]+"""
    return t


t_ignore = '\t \r'


def t_error(t):
    LexerError(t).handle()
    t.lexer.skip(1)


lexer = lex.lex()
