from issues.issue import Issue
from issues.manager import IssuesManager


class AssemblyError(Issue):
    def __str__(self) -> str:
        return f'ERROR {super().__str__()}'

    def handle(self):
        IssuesManager().add_error(self)
        return self
