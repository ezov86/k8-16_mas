from pattern_singleton import Singleton


class IssuesManager(metaclass=Singleton):
    def __init__(self):
        self.errors = []
        self.warnings = []

    def reset(self):
        self.errors = []
        self.warnings = []

    def has_errors(self) -> bool:
        return self.errors != []

    def has_warnings(self) -> bool:
        return not self.warnings != []

    def add_error(self, error):
        self.errors.append(error)

    def add_warning(self, warning):
        self.warnings.append(warning)

    def errors_to_str(self) -> str:
        return '\n'.join([str(error) for error in self.errors])

    def warnings_to_str(self) -> str:
        return '\n'.join([str(error) for error in self.warnings])  # pragma: no cover
