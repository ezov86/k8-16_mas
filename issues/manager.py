from pattern_singleton import Singleton


class IssuesManager:
    errors = []
    warnings = []

    @classmethod
    def reset(cls):
        cls.errors = []
        cls.warnings = []

    @classmethod
    def has_errors(cls) -> bool:
        return cls.errors != []

    @classmethod
    def has_warnings(cls) -> bool:
        return not cls.warnings != []

    @classmethod
    def add_error(cls, error):
        cls.errors.append(error)

    @classmethod
    def add_warning(cls, warning):
        cls.warnings.append(warning)

    @classmethod
    def errors_to_str(cls) -> str:
        return '\n'.join([str(error) for error in cls.errors])

    @classmethod
    def warnings_to_str(cls) -> str:
        return '\n'.join([str(error) for error in cls.warnings])
