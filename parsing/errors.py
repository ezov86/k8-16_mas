from issues.assembly_error import AssemblyError
from position import Position


class LexerError(AssemblyError):
    def __init__(self, token):
        self.token = token.value
        super().__init__(f'неверный токен "{token.value}"', Position.from_lex_token(token))


class InvalidSyntaxError(AssemblyError):
    def __init__(self, p):
        self.p = p.value
        super().__init__(f'неверный синтаксис в "{p.value}"', Position.from_parser_token(p))


class UnexpectedEofError(AssemblyError):
    def __init__(self):
        super().__init__('неожиданный конец файла')
