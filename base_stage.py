from issues.manager import IssuesManager


class BaseStage:
    def __init__(self):
        self.next = None

    def set_next(self, next_stage):
        self.next = next_stage
        return self.next

    def handle_issues(self):
        print(IssuesManager().warnings_to_str())

        if IssuesManager().has_errors():
            print(IssuesManager().errors_to_str())
            exit(-1)

    def handle(self, value):
        if self.next is None:
            return value

        return self.next.handle(value)
