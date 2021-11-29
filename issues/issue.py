from position import Position


class Issue:
    def __init__(self, msg: str, position: Position = None):
        self.msg = msg
        self.position = position

    def __str__(self):
        pos = '' if self.position is None else f'{str(self.position)}: '
        return f'{pos}{self.msg}.'
