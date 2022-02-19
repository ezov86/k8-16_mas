from typing import Optional

from cpu.manager import CpuConfigManager
from issues.assembly_error import AssemblyError
from position import Position
from preproc.errors import ReservedNameUsageError, RedefinitionError
from preproc.warnings import SameNameWarning, SpecialSymbolsInNameWarning


class DefNotFoundError(AssemblyError):
    def __init__(self, name: str, position: Position):
        self.name = name
        super().__init__(f'{name} не обнаружено в текущем контексте', position)


class DefsRepo:
    """
    Репозиторий с определениями (макрос, макроинструкция или метка).
    """

    def __init__(self):
        self.definitions: dict = {}
        self.builtin_names = [
            *CpuConfigManager.control_bits,
            '!nop'
        ]

    def add(self, definition, ignore_special_symbol=False):
        full_name = definition.full_name()

        if full_name in self.definitions:
            RedefinitionError(
                definition.full_name(),
                definition.position,
                self.definitions[full_name].position
            ).handle()
            return

        if definition.name in self.builtin_names:
            ReservedNameUsageError(definition.full_name(), definition.position).handle()
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
            SpecialSymbolsInNameWarning(name, '~', position).handle()


class LabelDefsRepo(DefsRepo):
    def add(self, definition, ignore_special_symbol=False):
        if not ignore_special_symbol:
            self.check_name_for_special_symbols(definition.local_name, definition.position)

        super().add(definition, ignore_special_symbol)


class DefsWithBodyRepo(DefsRepo):
    def __init__(self):
        super().__init__()

        self.another: Optional[DefsRepo] = None

    def add(self, definition, ignore_special_symbol=False):
        key = definition.full_name()
        if not ignore_special_symbol:
            self.check_name_for_special_symbols(key, definition.position)

        super().add(definition, ignore_special_symbol)

        if self.another is not None and self.another.is_in(key):
            SameNameWarning(key, definition.position, self.another.definitions[key].position).handle()
