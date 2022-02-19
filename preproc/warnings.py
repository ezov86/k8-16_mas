from issues.assembly_warning import AssemblyWarning
from position import Position


class SameNameWarning(AssemblyWarning):
    def __init__(self, name, position: Position, original_position: Position):
        self.name = name
        self.position = position
        self.original_position = original_position
        super().__init__(f'одно и то же имя "{name}" используется два раза для объявлений разных типов '
                         f'(первое использование в строке {original_position})', position)


class SpecialSymbolsInNameWarning(AssemblyWarning):
    def __init__(self, name: str, symbol: str, position: Position):
        super().__init__(f'в имени "{name}" используется незапрещённый спецсимвол "{symbol}"', position)
