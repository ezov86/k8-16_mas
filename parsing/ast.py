from typing import List
from position import Position


class BaseNode:
    def __init__(self, position: Position = None):
        self.position = position

    def set_position(self, position: Position):
        self.position = position
        return self


class BitMask(BaseNode):
    def __init__(self, name: str, params: List[str]):
        super().__init__()
        self.name = name
        self.params = params


class Microinstruction(BaseNode):
    def __init__(self, bit_masks: List[BitMask], label: str = '', next_microinstruction_label: str = ''):
        super().__init__()
        self.bit_masks = bit_masks
        self.label = label
        self.next_microinstruction_label = next_microinstruction_label


class Definition(BaseNode):
    def __init__(self, name: str, params: List[str], body: List[Microinstruction]):
        super().__init__()
        self.name = name
        self.params = params
        self.body = body


class MacrosDefinition(Definition):
    def __init__(self, name: str, params: List[str], body: List[Microinstruction], is_inline: bool = False):
        super().__init__(name, params, body)
        self.is_inline = is_inline


class MacroinstructionDefinition(Definition):
    pass


class Root(BaseNode):
    def __init__(self, macros_defs: List[MacrosDefinition], macroinstructions_defs: List[MacroinstructionDefinition]):
        super().__init__()
        self.macros_defs = macros_defs
        self.macroinstructions_defs = macroinstructions_defs
