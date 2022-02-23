from typing import List

from position import Position


class BaseNode:
    def __init__(self, position: Position = None):
        self.position = position


class BitMask(BaseNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class Label(BaseNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.is_local = name.startswith('.')


class Microinst(BaseNode):
    def __init__(self, bit_masks: List[BitMask], label_defs: List[str], next_microinst_label: Label = None):
        super().__init__()
        self.bit_masks = bit_masks
        self.label_defs = label_defs
        self.next_microinst_label = next_microinst_label


class MacrosDef(BaseNode):
    def __init__(self, name: str, body: List[Microinst], is_inline: bool = False):
        super().__init__()
        self.name = name
        self.body = body
        self.is_inline = is_inline


class MacroinstDef(BaseNode):
    def __init__(self, name: str, body: List[Microinst]):
        super().__init__()
        self.name = name
        self.body = body


class Root:
    def __init__(self, macros_defs: List[MacrosDef], macroinst_defs: List[MacroinstDef]):
        super().__init__()
        self.macros_defs = macros_defs
        self.macroinst_defs = macroinst_defs
