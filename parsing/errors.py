from issues.assembly_error import AssemblyError
from position import Position


class LexerError(AssemblyError):
    def __init__(self, token):
        super().__init__(f'invalid token "{token.value}"', Position.from_lex_token(token))


class InvalidSyntaxError(AssemblyError):
    def __init__(self, p):
        super().__init__(f'invalid syntax near "{p.value}"', Position.from_parser_token(p))


class UnexpectedEofError(AssemblyError):
    def __init__(self):
        super().__init__('unexpected end of file')
