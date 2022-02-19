from copy import copy
from typing import Optional

from def_repo import *
from parsing.ast import *
from preproc.errors import *
from preproc.pt import PreprocessedTree, LabelDef
from visitor import Visitor

Def = NewType('Def', Union[DefWithBody, LabelDef])


class AstToPt(Visitor):
    def __init__(self):
        self.last_relative_address = 0
        self.unique_label_id = 0

        self.labels = LabelDefsRepo()

        self.macros = DefsWithBodyRepo()
        self.macroinsts = DefsWithBodyRepo()
        self.macros.another = self.macroinsts
        self.macroinsts.another = self.macros

    def visit_bit_mask(self, n: BitMask, is_single: bool) -> List[BitMask]:
        definition = self.macros.find(n.full_name())
        if definition is None:
            # Битовая маска не является макросом.
            return [n]

        if not (definition.is_inline or is_single):
            # Использование многострочного макроса с другими масками в одной микроинструкции.
            MultilineMacrosUsedAsInlineError(definition.full_name(), n.position).handle()
            return []

        return definition.body[0].bit_masks

    def convert_macros_labels(self, macros: MacrosDef, parent_definition: DefWithBody) -> List[Microinst]:
        for label_def in list(self.labels.to_dict().values()):
            if label_def.parent == macros:
                new_name = f'{parent_definition.full_name()}~{label_def.name}~{self.unique_label_id}'
                new_label = LabelDef(
                    new_name,
                    label_def.name,
                    self.last_relative_address + label_def.relative_address,
                    parent_definition
                )
                new_label.set_pos(label_def.position)
                self.labels.add(new_label, ignore_special_symbol=True)

        new_microinst = []
        for microinst in macros.body:
            new_microinst += self.visit(microinst, parent_definition, conv_macros=True)

        return new_microinst

    def convert_next_microinst_label(self, label: Optional[Label], parent_name: str, conv_macros: bool) -> \
            Optional[Label]:
        if label is None or not label.is_local:
            return label

        new_label = copy(label)
        if label.name.startswith('.'):
            label_name = label.name[1:]
        else:
            label_name = label.name

        new_label.name = f'{parent_name}~{label_name}'

        if conv_macros:
            new_label.name += f'~{self.unique_label_id}'

        return new_label

    def visit_microinst(self, n: Microinst, parent_def: DefWithBody, conv_macros=False) -> List[Microinst]:
        """
        Обработка микроинструкции.
        :return: Возвращается список, так как при раскрытии многострочного макроса вставляется его тело, состоящее из
        нескольких микроинструкций. Иначе возвращается список из одной микроинструкции.
        """
        is_single = False
        expanding_macros = False
        body = []
        address_increase = 0

        if len(n.bit_masks) == 1:
            # Одна маска может быть признаком многострочного макроса.
            is_single = True

            macros = self.macros.find(n.bit_masks[0].full_name())
            if macros is not None and not macros.is_inline:
                # Эта микроинструкция раскрывается в многострочный макрос.
                if n.next_microinst_label is not None:
                    NextMicroinstLabelAfterMacrosError(n.position).handle()

                if isinstance(parent_def, MacrosDef) and parent_def.is_inline:
                    MultilineMacrosInInlineError(n.position).handle()

                body = self.convert_macros_labels(macros, parent_def)
                self.unique_label_id += 1
                expanding_macros = True
                address_increase = len(body)

        if not expanding_macros:
            address_increase = 1

            preproc_bit_masks = []
            for mask in n.bit_masks:
                preproc_bit_masks += self.visit(mask, is_single)

            microinst = copy(n)
            microinst.bit_masks = preproc_bit_masks
            microinst.next_microinst_label = self.convert_next_microinst_label(
                n.next_microinst_label,
                parent_def.name,
                conv_macros
            )

            body = [microinst]

        if n.label_def != '' and not conv_macros:
            error = False

            if n.label_def.startswith('.'):
                # Локальная метка.
                is_local = True
                full_label_name = f'{parent_def.full_name()}~{n.label_def[1:]}'
            else:
                # Глобальная.
                is_local = False

                if isinstance(parent_def, MacrosDef):
                    # В макросе.
                    error = True
                    GlobalLabelInMacrosError(n.label_def, parent_def.name, n.position).handle()

                full_label_name = n.label_def

            if not error:
                new_label = LabelDef(full_label_name, n.label_def, self.last_relative_address, parent_def)
                new_label.set_pos(n.position)
                new_label.is_local = is_local
                self.labels.add(new_label)

        if not conv_macros:
            self.last_relative_address += address_increase

        return body

    def visit_body(self, definition: DefWithBody) -> List[Microinst]:
        body = []

        for microinst in definition.body:
            body += self.visit(microinst, definition)

        return body

    def visit_macroinst_def(self, n: MacroinstDef):
        self.last_relative_address = 0

        macroinst = copy(n)
        macroinst.body = self.visit_body(n)
        self.macroinsts.add(macroinst)

    def visit_macros_def(self, n: MacrosDef):
        self.last_relative_address = 0
        n.body = self.visit_body(n)

        self.macros.add(n)

    def visit_root(self, n: Root) -> PreprocessedTree:
        for macros_def in n.macros_defs:
            self.visit(macros_def)

        for macroinstruction_def in n.macroinst_defs:
            self.visit(macroinstruction_def)

        # Удаление меток, которые объявлены в макросах.
        for name, label in list(self.labels.to_dict().items()):
            if label.is_in_macros():
                self.labels.remove(name)

        return PreprocessedTree(
            self.macroinsts,
            self.labels
        )
