import os

from context import Context

if os.path.isdir('parser_samples'):
    root_dir = ''  # pragma: no cover
else:
    root_dir = 'tests/'  # pragma: no cover


def new_context() -> Context:
    context = Context()
    # Чтобы продолжать работу теста при ошибках ассемблера и не выводить информацию в stdout.
    context.args.ignore_errors = True
    context.args_ignore_warnings = True
    return context


def get_path(test_name: str, path_in_test_dir: str) -> str:
    return f'{root_dir}{test_name}_samples/{path_in_test_dir}'


def get_test_path(test_name: str, path_in_samples_dir: str, is_valid: bool) -> str:
    if is_valid:
        path_in_test_dir = 'valid/'
    else:
        path_in_test_dir = 'invalid/'

    path_in_test_dir += f'{path_in_samples_dir}.mas'

    return get_path(test_name, path_in_test_dir)


def reset_lexer():
    pass


def tabs_to_spaces(text: str) -> str:
    return text.replace('\t', '    ')


def load_file(path: str) -> str:
    with open(path) as f:
        return f.read()
