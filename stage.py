from context import Context


class Stage:
    def __init__(self):
        self.next = None

    def set_next(self, next_stage):
        self.next = next_stage
        return self.next

    def check_for_issues(self, context: Context):
        if not context.args.ignore_warnings and context.has_warnings():
            print(*context.warnings, sep='\n')

        if not context.args.ignore_errors and context.has_errors():
            print(*context.errors, sep='\n')
            exit(-1)

    def handle(self, context: Context):
        self.check_for_issues(context)

        if self.next is None:
            return context

        return self.next.handle(context)
