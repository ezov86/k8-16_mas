from typing import Optional
from assembler_ast import *
from pt import PreprocessedTree, LabelDef

from visitor import Visitor


class PtToCode(Visitor):
    def __init__(self, tracking=False):
        self.tracking = tracking

    def visit_preprocessed_tree(self, n: PreprocessedTree) -> str:
        text = '# Labels:\n'
        text += '# name - address - parent\n'

        for label in n.labels.to_dict().values():
            text += self.visit(label) + '\n'

        text += '\n\n\n'
        text += '# Macroinstructions:\n'

        for macroinst in n.macroinst_defs.to_dict().values():
            text += self.visit(macroinst, n) + '\n\n'

        return text

    def visit_macroinst_def(self, n: MacroinstDef, pt: PreprocessedTree) -> str:
        labels = []

        for label in pt.labels.to_dict().values():
            if label.parent.full_name() == n.full_name():
                labels.append(label)

        body = ''
        address = 0
        for microinst in n.body:
            for label in labels:
                if label.relative_address == address:
                    body += f'{label.name.replace(" ", "~")}:\n'
            body += f'\t{self.visit(microinst)};'

            if self.tracking:
                body += f' # :{microinst.position}'

            body += '\n'

            address += 1

        return f'%i {n.full_name()} {{\n{body}}}'

    def visit_microinst(self, n: Microinst) -> str:
        text = ' | '.join([self.visit(bit_mask) for bit_mask in n.bit_masks])
        text += self.visit_label(n.next_microinst_label)

        return text

    def visit_label(self, n: Optional[Label]) -> str:
        if n is None:
            return ''

        return f' @{n.name}'

    def visit_bit_mask(self, n: BitMask) -> str:
        return n.full_name()

    def visit_label_def(self, n: LabelDef) -> str:
        return f'# {{{n.name}}} - {{{n.relative_address}}} - {{{n.parent.full_name()}}}'
