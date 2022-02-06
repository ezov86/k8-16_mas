from typing import List
from position import Position


class BaseNode:
    def __init__(self, position: Position = None):
        self.position = position

    def set_pos(self, position: Position):
        self.position = position
        return self


class BitMask(BaseNode):
    def __init__(self, name: str, params: List[str]):
        super().__init__()
        self.name = name
        self.params = params


class Microinst(BaseNode):
    def __init__(self, bit_masks: List[BitMask], label: str = '', next_microinst_label: str = ''):
        super().__init__()
        self.bit_masks = bit_masks
        self.label = label
        self.next_microinst_label = next_microinst_label


class Def(BaseNode):
    def __init__(self, name: str, params: List[str], body: List[Microinst]):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body

    def name_with_params(self) -> str:
        if self.params:
            params_str = f'({", ".join(self.params)})'
        else:
            params_str = ''

        return self.name + params_str


class MacrosDef(Def):
    def __init__(self, name: str, params: List[str], body: List[Microinst], is_inline: bool = False):
        super().__init__(name, params, body)
        self.is_inline = is_inline


class MacroinstDef(Def):
    pass


class Root(BaseNode):
    def __init__(self, macros_defs: List[MacrosDef], macroinst_defs: List[MacroinstDef]):
        super().__init__()
        self.macros_defs = macros_defs
        self.macroinst_defs = macroinst_defs
