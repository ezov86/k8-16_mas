from position import Position


class Issue:
    def __init__(self, msg: str, position: Position = None):
        self.msg = msg
        self.position = position

    def __str__(self):
        pos = '' if self.position is None else f'в строке {str(self.position)}: '
        return f'{pos}{self.msg}.'


class AssemblyWarning(Issue):
    def __str__(self):
        return f'ВНИМАНИЕ {super().__str__()}'


class AssemblyError(Issue):
    def __str__(self) -> str:
        return f'ОШИБКА {super().__str__()}'

