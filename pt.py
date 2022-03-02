from typing import List

import assembler_ast as ast
from position import Position


class BasePreprocNode:
    def __init__(self, pos: Position = None):
        self.position = pos


class Root:
    def __init__(self, macroinst_repo, labels_repo):
        super().__init__()
        self.macroinst_repo = macroinst_repo
        self.labels_repo = labels_repo


class Def(BasePreprocNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class DefWithAddress(Def):
    def __init__(self, name: str):
        super().__init__(name)
        self.address = 0


class LabelDef(DefWithAddress):
    def __init__(self, name: str, local_name: str, parent: Def, is_local=False):
        super().__init__(name)
        self.local_name = local_name
        self.parent = parent
        self.is_local = is_local

    def is_in_macros(self) -> bool:
        return isinstance(self.parent, MacrosDef)


class Microinst(BasePreprocNode):
    def __init__(self, bit_mask: List[ast.BitMask], label_defs: List[LabelDef], nm_label: ast.Label):
        super().__init__()
        self.bit_masks = bit_mask
        self.label_defs = label_defs
        self.nm_label = nm_label


class MacroinstDef(DefWithAddress):
    def __init__(self, name: str, body: List[Microinst]):
        super().__init__(name)
        self.body = body


class MacrosDef(Def):
    def __init__(self, name: str, body: List[Microinst], is_inline: bool = False):
        super().__init__(name)
        self.body = body
        self.is_inline = is_inline
