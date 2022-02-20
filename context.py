from typing import Union

from issue import AssemblyError, AssemblyWarning


class Args:
    def __init__(self):
        self.source_file_path = ''
        self.stop_after_parsing = False
        self.ignore_warnings = False
        self.use_csv = False
        self.use_intel_hex = False
        self.ignore_errors = False
        self.cpu_config_path = 'default_cpu_config.json'
        self.stop_after_preprocessing = False


class CpuConfig:
    def __init__(self):
        self.name = ''
        self.mi_bits = 0
        self.nmip_bits = 0
        self.inst_opc_bits = 0
        self.control_bits = []
        self.conflicting_control_bits = []


class Context:
    def __init__(self):
        self.errors = []
        self.warnings = []

        self.args = Args()
        self.ast = None
        self.cpu_config = CpuConfig()
        self.pt = None

    def handle_issue(self, issue: Union[AssemblyError, AssemblyWarning]):
        if isinstance(issue, AssemblyError):
            self.errors.append(issue)
        elif isinstance(issue, AssemblyWarning):
            self.warnings.append(issue)
        else:
            raise ValueError()

    def has_errors(self) -> bool:
        return len(self.errors) >= 1

    def has_warnings(self) -> bool:
        return len(self.warnings) >= 1

    def reset_issues(self):
        self.errors = []
        self.warnings = []
