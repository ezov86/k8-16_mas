class MicroinstBits:
    def __init__(self):
        self.control_bits = 0
        self.nmip = 0

    def get(self, index: int) -> int:
        return self.control_bits >> index & 1

    def set(self, index: int):
        self.control_bits |= (1 << index)

    def to_int(self, mi_adr_size: int) -> int:
        return self.control_bits << mi_adr_size | self.nmip

    def set_all_bits(self, value: int, mi_adr_size: int):
        self.control_bits = value >> mi_adr_size
        self.nmip = value & (mi_adr_size**2 - 1)
