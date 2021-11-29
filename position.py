class Position:
    def __init__(self, line: int):
        self.line = line

    def __str__(self):
        return f'at line {self.line}'

    @staticmethod
    def start():
        return Position(1)

    @staticmethod
    def from_parser_ctx(p):
        return Position.from_parser_token(p.slice[1])

    @staticmethod
    def from_parser_token(p):
        return Position(p.lineno)

    @staticmethod
    def from_lex_token(t):
        return Position(t.lineno)
