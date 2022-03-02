from context import Context
from microinst_bits import MicroinstBits
from output_generators.gen import OutputGenerator
import math


class BinaryOutputGenerator(OutputGenerator):
    def __init__(self, context: Context, output_path: str):
        super().__init__(context, output_path)
        self.file = open(output_path, 'wb')
        self.address = 0

    def begin(self):
        pass

    def write_bytes(self, value: int):
        order = 'big' if self.context.cpu_config.big_endian else 'little'
        self.file.write(value.to_bytes(math.ceil(self.context.cpu_config.get_microinst_size() / 8), order))

    def microinst(self, bits: MicroinstBits):
        self.write_bytes(bits.to_int(self.context.cpu_config.mi_adr_size))
        self.address += 1

    def macroinst_begin(self, macroinst_name: str):
        pass

    def macroinst_end(self, macroinst_name: str):
        pass

    def segment_gap(self, new_address: int):
        for _ in range(new_address - self.address):
            self.write_bytes(0)
