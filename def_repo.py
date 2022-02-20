from typing import Optional

from context import Context
from issue import AssemblyError, AssemblyWarning
from position import Position


class DefNotFoundError(AssemblyError):
    def __init__(self, name: str, position: Position):
        self.name = name
        super().__init__(f'{name} не обнаружено в текущем контексте', position)


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


class DefsRepo:
    """
    Репозиторий с определениями (макрос, макроинструкция или метка).
    """

    def __init__(self, context: Context):
        self.definitions: dict = {}
        self.context = context
        self.builtin_names = [
            *context.cpu_config.control_bits,
            '!nop'
        ]

    def add(self, definition, ignore_special_symbol=False):
        full_name = definition.full_name()

        if full_name in self.definitions:
            self.context.handle_issue(RedefinitionError(
                definition.full_name(),
                definition.position,
                self.definitions[full_name].position
            ))
            return

        if definition.name in self.builtin_names:
            self.context.handle_issue(ReservedNameUsageError(definition.full_name(), definition.position))
            return

        self.definitions[full_name] = definition

    def to_dict(self) -> dict:
        return self.definitions

    def find(self, full_name: str):
        try:
            return self.definitions[full_name]
        except KeyError:
            return None

    def is_in(self, full_name: str) -> bool:
        return self.find(full_name) is not None

    def find_or_fail(self, full_name: str, position_for_error):
        definition = self.find(full_name)

        if definition is None:
            DefNotFoundError(full_name, position_for_error)

        return definition

    def remove(self, full_name: str):
        del self.definitions[full_name]

    def check_name_for_special_symbols(self, name: str, position: Position):
        if '~' in name:
            self.context.handle_issue(SpecialSymbolsInNameWarning(name, '~', position))


class LabelDefsRepo(DefsRepo):
    def add(self, definition, ignore_special_symbol=False):
        if not ignore_special_symbol:
            self.check_name_for_special_symbols(definition.local_name, definition.position)

        super().add(definition, ignore_special_symbol)


class DefsWithBodyRepo(DefsRepo):
    def __init__(self, context: Context):
        super().__init__(context)

        self.another_repo: Optional[DefsRepo] = None

    def add(self, definition, ignore_special_symbol=False):
        key = definition.full_name()
        if not ignore_special_symbol:
            self.check_name_for_special_symbols(key, definition.position)

        super().add(definition, ignore_special_symbol)

        if self.another_repo is not None and self.another_repo.is_in(key):
            self.context.handle_issue(SameNameWarning(
                key,
                definition.position,
                self.another_repo.definitions[key].position
            ))
