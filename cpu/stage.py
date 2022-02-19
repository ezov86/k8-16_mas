from args.manager import ArgsManager
from base_stage import BaseStage
import json

from cpu.error import InvalidCpuConfigError
from cpu.manager import CpuConfigManager


class CpuConfigLoadingStage(BaseStage):
    """
    Этап загрузки конфигурации процессора.
    """

    def handle(self, ast):
        with open(ArgsManager.cpu_config_path) as file:
            text = file.read()

        try:
            dic = json.loads(text)
            CpuConfigManager.name = dic['name']
            CpuConfigManager.mi_bits = dic['mi_bits']
            CpuConfigManager.nmip_bits = dic['nmip_bits']
            CpuConfigManager.inst_opc_bits = dic['inst_opc_bits']
            CpuConfigManager.control_bits = dic['control_bits']
            CpuConfigManager.conflicting_control_bits = dic['conflicting_control_bits']

        except json.decoder.JSONDecodeError or KeyError:
            InvalidCpuConfigError().handle()

        super().handle_issues()

        return super().handle(ast)
