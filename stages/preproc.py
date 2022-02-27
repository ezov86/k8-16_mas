from copy import copy
from typing import NewType, Union, Optional

import pt
from assembler_ast import *
from context import Context
from def_repo import LabelDefsRepo, MacroinstOrMacrosDefRepo
from issue import AssemblyError
import assembler_ast as ast
from visitors.pt_to_code import PtToCode
from stage import Stage
from visitor import Visitor


class MultilineMacrosUsedAsInlineError(AssemblyError):
    def __init__(self, name: str, position: Position):
        self.name = name
        super().__init__(f'многострочный макрос "{name}" использован как однострочный', position)


class GlobalLabelInMacrosError(AssemblyError):
    def __init__(self, label_name: str, macros_name: str, position: Position):
        self.label_name = label_name
        self.macros_name = macros_name
        super().__init__(f'глобальная метка "{label_name}" объявлена в макросе "{macros_name}"', position)


class NextMicroinstLabelAfterMacrosError(AssemblyError):
    def __init__(self, position: Position):
        super().__init__(f'метка перехода установлена после макроса', position)


class MultilineMacrosInInlineError(AssemblyError):
    def __init__(self, position: Position):
        super().__init__(f'использование многострочного макроса в однострочном', position)


class Preprocessing(Stage):
    def handle(self, context: Context) -> Context:
        context.pt = AstToPt(context).visit(context.ast)

        if context.args.stop_after_preprocessing:
            print(PtToCode(tracking=True).visit(context.pt))
            super().check_for_issues(context)
            exit(0)

        return super().handle(context)


class AstToPt(Visitor):
    def __init__(self, context: Context):
        self.unique_label_id = 0

        self.context = context

        self.labels = LabelDefsRepo(context)
        self.macros = MacroinstOrMacrosDefRepo(context)
        self.macroinsts = MacroinstOrMacrosDefRepo(context)

        self.macros.another_repo = self.macroinsts
        self.macroinsts.another_repo = self.macros

    def visit_root(self, n: ast.Root) -> pt.Root:
        for macros_def in n.macros_defs:
            self.macros.add(self.visit(macros_def))

        for macroinst_def in n.macroinst_defs:
            self.macroinsts.add(self.visit(macroinst_def))

        # Удаление меток, которые объявлены в макросах.
        for name, label in list(self.labels.to_dict().items()):
            if label.is_in_macros():
                self.labels.remove(name)

        return pt.Root(
            self.macroinsts,
            self.labels
        )

    def visit_macros_def(self, n: ast.MacrosDef) -> pt.MacrosDef:
        macros = pt.MacrosDef(n.name, [], n.is_inline)
        macros.body = self.visit_body(n.body, macros)
        macros.position = n.position
        return macros

    def visit_macroinst_def(self, n: ast.MacroinstDef) -> pt.MacroinstDef:
        macroinst = pt.MacroinstDef(n.name, [])
        macroinst.body = self.visit_body(n.body, macroinst)
        macroinst.position = n.position
        return macroinst

    def visit_body(self, body: List[ast.Microinst], parent_def: pt.Def) -> List[pt.Microinst]:
        visited_body = []
        for mi in body:
            visited_body += self.visit(mi, parent_def)

        return visited_body

    def visit_microinst(self, n: ast.Microinst, parent_def: pt.Def) -> List[pt.Microinst]:
        if len(n.bit_masks) == 1:
            macros = self.macros.find(n.bit_masks[0].name)
            if macros is not None and not macros.is_inline:
                # Эта микроинструкция раскрывается в многострочный макрос.
                if n.next_microinst_label is not None:
                    self.context.handle_issue(NextMicroinstLabelAfterMacrosError(n.position))

                if isinstance(parent_def, pt.MacrosDef) and parent_def.is_inline:
                    self.context.handle_issue(MultilineMacrosInInlineError(n.position))

                body = self.convert_macros_body(macros, parent_def)
                body[0].label_defs += self.get_label_defs(n.label_defs, parent_def, n.position)

                self.unique_label_id += 1
                return body

        bit_masks = []
        for bm in n.bit_masks:
            bit_masks += self.visit(bm)

        if n.next_microinst_label is not None:
            nmi_label = copy(n.next_microinst_label)
            if n.next_microinst_label.is_local:
                nmi_label.name = f'{parent_def.name}~{n.next_microinst_label.name[1:]}'
            else:
                nmi_label.name = n.next_microinst_label.name
        else:
            nmi_label = None

        label_defs = self.get_label_defs(n.label_defs, parent_def, n.position)

        mi = pt.Microinst(bit_masks, label_defs, nmi_label)
        mi.position = n.position

        return [mi]

    def visit_bit_mask(self, n: ast.BitMask) -> [ast.BitMask]:
        macros = self.macros.find(n.name)
        if macros is None:
            return [n]

        if not macros.is_inline:
            self.context.handle_issue(MultilineMacrosUsedAsInlineError(macros.name, n.position))
            return []

        return macros.body[0].bit_masks

    def get_label_defs(self, label_defs_names: List[str], parent_def: pt.Def, pos: Position) -> List[pt.LabelDef]:
        label_defs = []
        for local_name in label_defs_names:
            if local_name.startswith('.'):
                # Объявление локальной метки.
                is_local = True
                name = f'{parent_def.name}~{local_name[1:]}'
            else:
                # Глобальная метка
                if isinstance(parent_def, pt.MacrosDef):
                    # Объявление глобальной метки в макросе запрещено.
                    self.context.handle_issue(GlobalLabelInMacrosError(local_name, parent_def.name, pos))
                    return []

                is_local = False
                name = local_name

            label_def = pt.LabelDef(name, local_name, parent_def, is_local)
            label_def.position = pos

            label_defs.append(label_def)
            self.labels.add(label_def)

        return label_defs

    def convert_macros_body(self, macros: pt.MacrosDef, parent_def: pt.Def) -> List[ast.Microinst]:
        if macros.is_inline:
            # Если это однострочный макрос, то преобразование меток не требуется.
            return macros.body

        conv_body = []
        for mi in macros.body:
            new_mi = copy(mi)

            # Преобразование объявлений меток.
            new_label_defs = []
            for label in mi.label_defs:
                new_def = copy(label)
                new_def.name = f'{parent_def.name}~{new_def.name}~{self.unique_label_id}'

                new_label_defs.append(new_def)
                self.labels.add(new_def, ignore_spec_symbol=True)

            new_mi.label_defs = new_label_defs

            # Преобразование меток переходов.
            if mi.nm_label is not None:
                new_nm_label = copy(mi.nm_label)
                if mi.nm_label.is_local:
                    new_nm_label.name = f'{parent_def.name}~{new_nm_label.name}~{self.unique_label_id}'
                else:
                    new_nm_label.name = new_nm_label.name

                new_mi.nm_label = new_nm_label

            conv_body.append(new_mi)

        return conv_body
