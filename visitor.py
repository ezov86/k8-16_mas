import inflection


class Visitor:
    def visit(self, node, *args, **kwargs):
        name = 'visit_' + inflection.underscore(node.__class__.__name__)
        if not hasattr(self, name):
            return self.visit_default(node, *args, **kwargs)

        return getattr(self, name)(node, *args, **kwargs)

    def visit_default(self, node, *args, **kwargs):
        raise NotImplementedError(f'No visit method found for \'{node.__class__.__name__}\'.')
