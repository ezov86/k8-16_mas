import assembler_ast as ast
from microinst_bits import MicroinstBits
from context import Context
from issue import AssemblyError, AssemblyWarning
from output_generators.bin_gen import BinaryOutputGenerator
from output_generators.csv_gen import CsvOutputGenerator
from output_generators.gen import OutputGenerator
from position import Position
import pt
from stage import Stage
from visitor import Visitor


class AddressOverflowError(AssemblyError):
    def __init__(self, address: int):
        self.address = address
        super().__init__(f'переполнение: ассемблер достиг адреса {hex(address)}. Микропрограмма имеет слишком большой '
                         f'размер для такой конфигурации')


class LabelNotFoundError(AssemblyError):
    def __init__(self, label_name: str, pos: Position):
        super().__init__(f'метка "{label_name}" не найдена', pos)


class BitMaskNotFoundError(AssemblyError):
    def __init__(self, bit_mask_full_name: str, pos: Position):
        self.bit_mask_full_name = bit_mask_full_name
        super().__init__(f'битовая маска "{bit_mask_full_name}" не найдена в конфигурации', pos)


class BitMaskMultipleUsageWarning(AssemblyWarning):
    def __init__(self, bit_mask_full_name, pos: Position):
        self.bit_mask_full_name = bit_mask_full_name
        super().__init__(f'битовая маска "{bit_mask_full_name}" используется более одного раза в микроинструкции', pos)


class DirectiveInvalidUsageError(AssemblyError):
    def __init__(self, directive_name: str, pos: Position):
        self.directive_name = directive_name
        super().__init__(f'директива "{directive_name}" использована неправильно (вместе с другими масками или без '
                         f'параметров)', pos)


class ValueOutOfRangeError(AssemblyError):
    def __init__(self, value: int, pos: Position):
        self.value = value
        super().__init__(f'директива !val имеет аргумент со значением {hex(value)}, '
                         f'превосходящим максимально допустимое в данной архитектуре', pos)


class CodeGeneration(Stage):
    def handle(self, context: Context):
        generators = {
            'csv': CsvOutputGenerator,
            'bin': BinaryOutputGenerator
        }

        gen_class = generators[context.args.generator]

        FirstPass(context).visit(context.pt)
        SecondPass(context, gen_class(context, context.args.output_file_path)).visit(context.pt)

        super().handle(context)


class FirstPass(Visitor):
    """ Первый проход ассемблера. Здесь макроинструкциям и меткам выдаются адреса.  """

    def __init__(self, context: Context):
        self.context = context

        self.control_bits_size = len(context.cpu_config.ctrl_bits_names)
        self.segment_size = context.cpu_config.inst_opc_size
        self.offset_size = context.cpu_config.mi_adr_size - self.segment_size

        self.offset = 0
        self.segment = 0

    def get_address(self) -> int:
        # Адрес состоит из:
        #  * Сегмента (offset) - старшие биты, изменяются при переходе на генерацию другой макроинструкции или при
        #  переполнении относительного адреса.
        #  * Смещения (offset) - младшие биты, изменяются при переходе на генерацию другой микроинструкции. При начале
        #  генерации новой макроинструкции сбрасываются до 0;
        #
        # Пример для K8-16:
        #  segment  offset
        # 00000000 : 0000
        #  8 бита   4 бита
        #
        # В K8-16 при обработке инструкции в микропрограмме происходит переход на адрес, в котором сегмент состоит из
        # опкода (тоже 8 бит), а смещение (оставшиеся 4 бита) равно 0.
        return self.segment << self.offset_size | self.offset

    def next_segment(self):
        self.offset = 0
        self.segment += 1

    def inc_address(self):
        if self.offset == 2 ** self.offset_size - 1:
            # Конец сегмента, смещение сбрасывается.

            if self.segment == 2 ** self.segment_size - 1:
                # Если это последний сегмент, то произошло переполнение адреса.
                raise OverflowError()

            self.next_segment()
        else:
            self.offset += 1

    def visit_root(self, n: pt.Root):
        try:
            for macroinst in n.macroinst_repo.to_dict().values():
                self.visit(macroinst)
        except OverflowError:
            self.context.handle_issue(AddressOverflowError(self.get_address() + 1))

    def visit_macroinst_def(self, n: pt.MacroinstDef):
        n.address = self.get_address()

        for mi in n.body:
            self.visit(mi)

        self.next_segment()

    def visit_microinst(self, n: pt.Microinst):
        for label_def in n.label_defs:
            label_def.address = self.get_address()

        self.inc_address()


class SecondPass(Visitor):
    def __init__(self, context: Context, gen: OutputGenerator):
        self.context = context
        self.cpu_config = context.cpu_config
        self.gen = gen
        self.cur_address = 0
        self.labels = context.pt.labels_repo

    def visit_root(self, n: pt.Root):
        self.gen.begin()

        for macroinst in n.macroinst_repo.to_dict().values():
            self.visit(macroinst)

    def visit_macroinst_def(self, n: pt.MacroinstDef):
        self.cur_address = n.address
        self.gen.segment_gap(self.cur_address)
        self.gen.macroinst_begin(n.name)

        for mi in n.body:
            self.visit(mi)

        self.gen.macroinst_end(n.name)

    def visit_microinst(self, n: pt.Microinst):
        bits = MicroinstBits()

        if len(n.bit_masks) == 1 and n.bit_masks[0].name == '!nop':
            # Директива !nop.
            bits.set_all_bits(
                self.cpu_config.nop_value,
                self.cpu_config.mi_adr_size
            )
        elif len(n.bit_masks) == 2 and n.bit_masks[0].name == '!val' and n.nm_label is None:
            # Директива !val
            try:
                value = int(n.bit_masks[1].name, base=16)
            except ValueError:
                self.context.handle_issue(DirectiveInvalidUsageError('!val', n.position))

                # Чтобы продолжить работу даже в случае ошибки.
                value = 0

            if value >= 2 ** self.cpu_config.get_microinst_size():
                self.context.handle_issue(ValueOutOfRangeError(value, n.position))

            bits.set_all_bits(
                value,
                self.cpu_config.mi_adr_size
            )
        else:
            # Обычная микроинструкция.
            for bm in n.bit_masks:
                self.visit(bm, bits)

            if n.nm_label is None:
                bits.nmip = self.cur_address + 1
            else:
                label_def = self.labels.find_or_fail(n.nm_label.name, n.position)
                if label_def is not None:
                    bits.nmip = label_def.address

        self.cur_address += 1

        self.gen.microinst(bits)

    def visit_bit_mask(self, n: ast.BitMask, bits: MicroinstBits):
        if n.name == '!nop' or n.name == '!val':
            self.context.handle_issue(DirectiveInvalidUsageError(n.name, n.position))
            return

        try:
            i = self.cpu_config.ctrl_bits_names.index(n.name)
        except ValueError:
            self.context.handle_issue(BitMaskNotFoundError(n.name, n.position))
            return

        if bits.get(i) == 1:
            self.context.handle_issue(BitMaskMultipleUsageWarning(n.name, n.position))
        else:
            bits.set(i)
