import os

from args.manager import ArgsManager
from parsing.lexer import lexer

ArgsManager.ignore_errors = True  # Чтобы продолжать работу теста при ошибке ассемблера.

if os.path.isdir('parser_samples'):
    root_dir = ''  # pragma: no cover
else:
    root_dir = 'tests/'  # pragma: no cover


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
    lexer.lineno = 1
