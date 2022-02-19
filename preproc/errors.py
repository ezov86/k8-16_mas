from issues.assembly_error import AssemblyError
from position import Position


class MultilineMacrosUsedAsInlineError(AssemblyError):
    def __init__(self, name: str, position: Position):
        self.name = name
        super().__init__(f'многострочный макрос "{name}" использован как однострочный', position)


class RedefinitionError(AssemblyError):
    def __init__(self, name: str, redefinition_position: Position, original_position: Position):
        self.name = name
        self.original_position = original_position
        super().__init__(f'переопределение "{name}" (изначально объявлено в строке {original_position})',
                         redefinition_position)


class ReservedNameUsageError(AssemblyError):
    def __init__(self, name: str, position: Position):
        self.name = name
        super().__init__(f'имя "{name}" зарезервировано', position)


class GlobalLabelInMacrosError(AssemblyError):
    def __init__(self, label_name: str, macros_name: str, position: Position):
        self.label_name = label_name
        self.macros_name = macros_name
        super().__init__(f'глобальная метка "{label_name}" объявлена в макросе "{macros_name}"', position)


class NextMicroinstLabelAfterMacrosError(AssemblyError):
    def __init__(self, position: Position):
        super().__init__(f'метка перехода установлена после макроса', position)


class MultilineMacrosInInlineError(AssemblyError):
    def __init__(self, position: Position):
        super().__init__(f'использование многострочного макроса в однострочном', position)
