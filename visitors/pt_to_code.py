import assembler_ast as ast
import pt

from visitor import Visitor


class PtToCode(Visitor):
    def __init__(self, tracking=False):
        self.tracking = tracking
        self.text = ''

    def visit_root(self, n: pt.Root):
        for macroinst in n.macroinst_repo.to_dict().values():
            self.visit(macroinst)
            self.add_line()

        return self.text

    def visit_label_def(self, n: pt.LabelDef):
        self.add_line(f'{n.name}  --  {n.parent.name}')

    def visit_macroinst_def(self, n: pt.MacroinstDef):
        self.add_line(f'%i {n.name} {{')

        for microinst in n.body:
            self.visit(microinst)

        self.add_line('}')

    def visit_microinst(self, n: pt.Microinst):
        if n.label_defs:
            label_names = []
            for label_def in n.label_defs:
                label_names.append(label_def.name)

            self.add_text(', '.join(label_names))
            self.add_line(':')

        self.add_text('\t')

        bit_masks_names = []
        for bit_mask in n.bit_masks:
            bit_masks_names.append(bit_mask.name)

        self.add_text(' | '.join(bit_masks_names))

        if n.nm_label is not None:
            self.add_text(f' @{n.nm_label.name}')

        self.add_line(';')

    def add_text(self, s: str):
        self.text += s

    def add_line(self, s: str = ''):
        self.add_text(s + '\n')
