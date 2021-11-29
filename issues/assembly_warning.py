from issue import Issue
from issues.manager import IssuesManager


class AssemblyWarning(Issue):
    def __str__(self):
        return f'WARNING {super().__str__()}'

    def handle(self):
        IssuesManager().add_warning(self)
        return self
