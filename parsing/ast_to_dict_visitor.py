from parsing.ast import *
from visitor import Visitor


class AstToDictVisitor(Visitor):
    def __init__(self, tracking=False):
        self.tracking = tracking

    def visit(self, n: BaseNode, *args, **kwargs) -> dict:
        r = super().visit(n, *args, **kwargs)

        if self.tracking:
            dic = {'node_type': n.__class__.__name__, 'line': n.position.line, **r}
        else:
            dic = r

        return dic

    def visit_bit_mask(self, n: BitMask) -> dict:
        return {
            'name': n.name,
            'params': n.params
        }

    def visit_microinstruction(self, n: Microinstruction) -> dict:
        return {
            'bit_masks': [self.visit(bit_mask) for bit_mask in n.bit_masks],
            'label': n.label,
            'next_microinstruction_label': n.next_microinstruction_label
        }

    def visit_definition(self, n: Definition) -> dict:
        return {
            'name': n.name,
            'params': n.params,
            'microinstructions': [self.visit(microinstruction) for microinstruction in n.body]
        }

    def visit_macros_definition(self, n: MacrosDefinition) -> dict:
        return {
            **self.visit_definition(n),
            'is_inline': n.is_inline
        }

    def visit_macroinstruction_definition(self, n: MacroinstructionDefinition) -> dict:
        return self.visit_definition(n)

    def visit_default(self, node, *args, **kwargs):
        return node

    def visit_root(self, node: Root) -> dict:
        return {
            'macros_defs': [self.visit(macros_def) for macros_def in node.macros_defs],
            'macroinstructions_defs':
                [self.visit(macroinstruction) for macroinstruction in node.macroinstructions_defs]
        }
