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
            context.cpu_config.from_dict(dic)

        except json.decoder.JSONDecodeError or KeyError:
            context.handle_issue(InvalidCpuConfigError())

        return super().handle(context)
