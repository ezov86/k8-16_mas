from assembler_ast import DefWithBody, MacrosDef
from def_repo import DefsRepo


class PreprocessedTree:
    def __init__(self, macroinst_defs: DefsRepo, labels: DefsRepo):
        super().__init__()
        self.macroinst_defs = macroinst_defs
        self.labels = labels


class LabelDef(DefWithBody):
    def __init__(self, full_name: str, local_name: str, relative_address: int, parent: DefWithBody, is_local=False):
        super().__init__(full_name, [], [])
        self.local_name = local_name
        self.relative_address = relative_address
        self.parent = parent
        self.is_local = is_local

    def is_in_macros(self) -> bool:
        return isinstance(self.parent, MacrosDef)
