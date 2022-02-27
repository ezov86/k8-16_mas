from context import Context
from issue import AssemblyError
from stage import Stage
import json


class InvalidCpuConfigError(AssemblyError):
    def __init__(self):
        super().__init__('неверный формат конфигурацинного файла')


class CpuConfigLoading(Stage):
    """
    Этап загрузки конфигурации процессора.
    """

    def handle(self, context: Context):
        with open(context.args.cpu_config_path) as file:
            text = file.read()

        try:
            dic = json.loads(text)
            context.cpu_config.name = dic['name']
            context.cpu_config.nmip_bits = dic['nmip_bits']
            context.cpu_config.inst_opc_bits = dic['inst_opc_bits']
            context.cpu_config.control_bits = dic['control_bits']
            context.cpu_config.conflicting_control_bits = dic['conflicting_control_bits']

        except json.decoder.JSONDecodeError or KeyError:
            context.handle_issue(InvalidCpuConfigError())

        return super().handle(context)
