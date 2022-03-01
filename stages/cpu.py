from context import Context
from issue import AssemblyError
from stage import Stage
import json


class InvalidCpuConfigError(AssemblyError):
    def __init__(self, message: str):
        super().__init__(f'неверный формат конфигурационного файла: {message}')


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

        except json.decoder.JSONDecodeError:
            context.handle_issue(InvalidCpuConfigError('ошибка при разборе JSON'))
        except TypeError:
            context.handle_issue(InvalidCpuConfigError('поле имеет неверный тип'))
        except KeyError:
            context.handle_issue(InvalidCpuConfigError('поле с именем не найдено'))

        return super().handle(context)
