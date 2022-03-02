from microinst_bits import MicroinstBits
from context import Context


class OutputGenerator:
    def __init__(self, context: Context, output_path: str):
        self.context = context
        self.output_path = output_path

    def begin(self):
        pass

    def microinst(self, bits: MicroinstBits):
        pass

    def macroinst_begin(self, macroinst_name: str):
        pass

    def macroinst_end(self, macroinst_name: str):
        pass

    def segment_gap(self, new_address: int):
        pass
