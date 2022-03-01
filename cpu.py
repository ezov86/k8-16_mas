from typing import List

from microinst_bits import MicroinstBits


class ControlBitsConflict:
    def __init__(self):
        self.one_of_bits = []
        self.all_bits = []

    def find_conflicting_bits(self, mi_bits: MicroinstBits, bit_names: List[str]) -> List[str]:
        for bit in self.all_bits:
            if not (mi_bits.get(bit) == 1):
                # Если хотя бы одно из условий не выполняется, то дальнейшая проверка не требуется.
                return []

        possible_conflicts = []
        for bit in self.one_of_bits:
            if mi_bits.get(bit) == 1:
                possible_conflicts.append(bit_names[bit])

        if len(possible_conflicts) <= 1:
            # Найден только один установленный бит, значит конфликта нет.
            return []

        return possible_conflicts

    def from_dict(self, d: dict, config):
        for bit in d['one_of']:
            self.one_of_bits.append(config.get_cont_bit_index(bit))

        for bit in d['all']:
            self.all_bits.append(config.get_cont_bit_index(bit))


class CpuConfig:
    def __init__(self):
        self.name = ''
        self.mi_adr_size = 0
        self.inst_opc_size = 0
        self.ctrl_bits_names = []
        self.conflicts = []

    def get_microinst_size(self) -> int:
        return len(self.ctrl_bits_names) + self.mi_adr_size

    def get_cont_bit_index(self, name: str) -> int:
        i = self.ctrl_bits_names.index(name)

        return i

    def find_conflicting_bits(self, mi_bits: MicroinstBits) -> List[str]:
        found_conflicts = []
        for conflict in self.conflicts:
            found_conflicts += conflict.find_conflicting_bits(mi_bits, self.ctrl_bits_names)

        return found_conflicts

    def from_dict(self, d: dict):
        self.name = d['name']
        self.mi_adr_size = d['mi_adr_size']
        self.inst_opc_size = d['inst_opc_size']
        self.ctrl_bits_names = d['ctrl_bits_names']

        for conf_dict in d['conflicts']:
            self.conflicts.append(ControlBitsConflict().from_dict(conf_dict, self))
