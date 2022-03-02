import csv

from microinst_bits import MicroinstBits
from context import Context
from output_generators.gen import OutputGenerator


class CsvOutputGenerator(OutputGenerator):
    def __init__(self, context: Context, output_path: str):
        super().__init__(context, output_path)

        self.file = open(output_path, 'w', newline='')
        self.csv = csv.writer(self.file)

        self.address = 0

    def begin(self):
        self.csv.writerow(['address'] + self.context.cpu_config.ctrl_bits_names + ['nmip'])

    def microinst(self, bits: MicroinstBits):
        bits_list = []
        for i in range(len(self.context.cpu_config.ctrl_bits_names)):
            bits_list.append(bits.get(i))

        self.csv.writerow([hex(self.address)] + bits_list + [hex(bits.nmip)])
        self.address += 1

    def macroinst_begin(self, macroinst_name: str):
        self.csv.writerow([f'%i {macroinst_name}'])

    def macroinst_end(self, macroinst_name: str):
        pass

    def segment_gap(self, new_address: int):
        for _ in range(new_address - self.address):
            self.microinst(MicroinstBits())
