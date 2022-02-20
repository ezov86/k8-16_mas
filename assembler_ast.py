from typing import List

from position import Position


class BaseNode:
    def __init__(self, position: Position = None):
        self.position = position

    def set_pos(self, position: Position):
        self.position = position
        return self


class NamedNode(BaseNode):
    def full_name(self) -> str:
        """ abstract """
        raise NotImplementedError()


class OnlyNameNode(BaseNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def full_name(self) -> str:
        return self.name


class NamedNodeWithParams(BaseNode):
    def __init__(self, name: str, params: List[str]):
        super().__init__()
        self.name = name
        self.params = params

    def full_name(self) -> str:
        if self.params:
            params_str = f'({", ".join(self.params)})'
        else:
            params_str = ''

        return self.name + params_str


class BitMask(NamedNodeWithParams):
    def __init__(self, name: str, params: List[str]):
        super().__init__(name, params)


class Label(BaseNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.is_local = name.startswith('.')


class Microinst(BaseNode):
    def __init__(self, bit_masks: List[BitMask], label_def: str = '', next_microinst_label: Label = None):
        super().__init__()
        self.bit_masks = bit_masks
        self.label_def = label_def
        self.next_microinst_label = next_microinst_label


class DefWithBody(NamedNodeWithParams):
    def __init__(self, name: str, params: List[str], body: List[Microinst]):
        super().__init__(name, params)
        self.body = body


class MacrosDef(DefWithBody):
    def __init__(self, name: str, params: List[str], body: List[Microinst], is_inline: bool = False):
        super().__init__(name, params, body)
        self.is_inline = is_inline


class MacroinstDef(DefWithBody):
    pass


class Root(BaseNode):
    def __init__(self, macros_defs: List[MacrosDef], macroinst_defs: List[MacroinstDef]):
        super().__init__()
        self.macros_defs = macros_defs
        self.macroinst_defs = macroinst_defs
