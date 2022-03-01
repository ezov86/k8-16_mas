from typing import Optional, Dict, Union

import pt
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
        self.defs: Dict[str, pt.Def] = {}
        self.context = context
        self.builtin_names = [
            *context.cpu_config.ctrl_bits_names,
            '!nop',
            '!val'
        ]

    def add(self, d: pt.Def, ignore_spec_symbol=False):
        if not ignore_spec_symbol:
            self.check_spec_symbol(d)

        if d.name in self.defs:
            self.context.handle_issue(RedefinitionError(
                d.name,
                d.position,
                self.defs[d.name].position
            ))
            return

        if d.name in self.builtin_names:
            self.context.handle_issue(ReservedNameUsageError(d.name, d.position))
            return

        self.defs[d.name] = d

    def to_dict(self) -> dict:
        return self.defs

    def find(self, full_name: str):
        try:
            return self.defs[full_name]
        except KeyError:
            return None

    def is_in(self, name: str) -> bool:
        return name in self.defs

    def find_or_fail(self, name: str, pos: Position):
        d = self.find(name)

        if d is None:
            self.context.handle_issue(DefNotFoundError(name, pos))

        return d

    def remove(self, name: str):
        del self.defs[name]

    def check_spec_symbol(self, d: pt.Def):
        if '~' in d.name:
            self.context.handle_issue(SpecialSymbolsInNameWarning(d.name, '~', d.position))


class LabelDefsRepo(DefsRepo):
    def check_spec_symbol(self, d: pt.LabelDef):
        if '~' in d.local_name:
            self.context.handle_issue(SpecialSymbolsInNameWarning(d.local_name, '~', d.position))


class MacroinstOrMacrosDefRepo(DefsRepo):
    def __init__(self, context: Context):
        super().__init__(context)
        self.another_repo: Optional[DefsRepo] = None

    def add(self, d: Union[pt.MacrosDef, pt.MacroinstDef], ignore_spec_symbol=False):
        super().add(d, ignore_spec_symbol)

        if self.another_repo is not None and self.another_repo.is_in(d.name):
            self.context.handle_issue(SameNameWarning(
                d.name,
                d.position,
                self.another_repo.defs[d.name].position
            ))
