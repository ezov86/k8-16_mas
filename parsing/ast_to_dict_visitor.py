from typing import Optional

from parsing.ast import *
from visitor import Visitor


class AstToDictVisitor(Visitor):
    def __init__(self, tracking=False):
        self.tracking = tracking

    def visit(self, n, *args, **kwargs) -> dict:
        r = super().visit(n, *args, **kwargs)

        if isinstance(n, BaseNode) and self.tracking:
            dic = {'node_type': n.__class__.__name__, 'line': n.position.line, **r}
        else:
            dic = r

        return dic

    def visit_none_type(self, n: None) -> None:
        return n

    def visit_bit_mask(self, n: BitMask) -> dict:
        return {
            'name': n.name,
            'params': n.params
        }

    def visit_microinst(self, n: Microinst) -> dict:
        return {
            'bit_masks': [self.visit(bit_mask) for bit_mask in n.bit_masks],
            'label_def': n.label_def,
            'next_microinstruction_label': self.visit(n.next_microinst_label)
        }

    def visit_def(self, n: DefWithBody) -> dict:
        return {
            'name': n.name,
            'params': n.params,
            'microinstructions': [self.visit(microinstruction) for microinstruction in n.body]
        }

    def visit_macros_def(self, n: MacrosDef) -> dict:
        return {
            **self.visit_def(n),
            'is_inline': n.is_inline
        }

    def visit_macroinst_def(self, n: MacroinstDef) -> dict:
        return self.visit_def(n)

    def visit_root(self, node: Root) -> dict:
        return {
            'macros_defs': [self.visit(macros_def) for macros_def in node.macros_defs],
            'macroinst_defs':
                [self.visit(macroinstruction) for macroinstruction in node.macroinst_defs]
        }

    def visit_label(self, node: Label) -> dict:
        return {
            'name': node.name,
            'is_local': node.is_local
        }
