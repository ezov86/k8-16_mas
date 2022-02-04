import os

from args.manager import ArgsManager

ArgsManager.ignore_errors = True  # Чтобы продолжать работу теста при ошибке ассемблера.

if os.path.isdir('parser_samples'):
    root_dir = ''  # pragma: no cover
else:
    root_dir = 'tests/'  # pragma: no cover


def get_path(test_name: str, path_in_samples_dir: str, is_valid: bool) -> str:
    s = f'{root_dir}{test_name}_samples/'
    if is_valid:
        s += 'valid/'
    else:
        s += 'invalid/'

    s += f'{path_in_samples_dir}.mas'

    return s
