from issues.assembly_error import AssemblyError


class InvalidCpuConfigError(AssemblyError):
    def __init__(self):
        super().__init__('неверный формат конфигурацинного файла')
