import helpers
from stages.cpu import CpuConfigLoadingStage
from def_repo import ReservedNameUsageError, RedefinitionError, SpecialSymbolsInNameWarning, SameNameWarning

from stages.parsing import CodeParsing
from stages.preproc import *


def get_preproc_sample_path(path_in_samples_dir: str, is_valid: bool) -> str:
    return helpers.get_test_path('preproc', path_in_samples_dir, is_valid)


pas = CodeParsing()
ccs = CpuConfigLoadingStage()
prs = PreprocessingStage()

pas.set_next(ccs).set_next(prs)


def preprocess(path: str) -> Context:
    context = helpers.new_context()
    context.args.source_file_path = path
    context.args.cpu_config_path = helpers.get_path('preproc', 'test_config.json')

    context = pas.handle(context)
    helpers.reset_lexer()

    return context


def assert_issues(sample_name: str, expected_issues: list):
    context = preprocess(get_preproc_sample_path(sample_name, is_valid=False))
    real_issues = context.errors + context.warnings

    assert len(real_issues) == len(expected_issues)
    for expected_error, real_error in zip(real_issues, expected_issues):
        assert str(real_error) == str(expected_error)

    helpers.reset_lexer()


def test_invalid_reserved_name_usage():
    assert_issues('reserved_name_usage', [
        ReservedNameUsageError('b', Position(1)),
        ReservedNameUsageError('c(1)', Position(5)),
        ReservedNameUsageError('!nop', Position(9)),
        ReservedNameUsageError('d(1, 2)', Position(7)),
        ReservedNameUsageError('c', Position(14)),
        ReservedNameUsageError('a', Position(12)),
        ReservedNameUsageError('d', Position(19)),
        ReservedNameUsageError('!nop', Position(17))
    ])


def test_invalid_redefinition():
    assert_issues('redefinition', [
        RedefinitionError('mm1', Position(5), Position(1)),
        RedefinitionError('mm1(a, b)', Position(14), Position(10)),
        RedefinitionError('mi1', Position(21), Position(20)),
        RedefinitionError('mi1(a, b)', Position(24), Position(23)),
        RedefinitionError('i1', Position(32), Position(28)),
        RedefinitionError('i1(a, b)', Position(41), Position(37)),
        RedefinitionError('l', Position(49), Position(44)),
        RedefinitionError('i2~l', Position(53), Position(51))
    ])


def test_invalid_multiline_macros_used_as_inline():
    assert_issues('multiline_macros_used_as_inline', [
        MultilineMacrosUsedAsInlineError('m', Position(6))
    ])


def test_invalid_global_label_in_macros():
    assert_issues('global_label_in_macros', [
        GlobalLabelInMacrosError('l', 'm', Position(3))
    ])


def test_invalid_next_microinst_label_after_macros():
    assert_issues('next_microinst_label_after_macros', [
        NextMicroinstLabelAfterMacrosError(Position(9))
    ])


def test_invalid_multiline_macros_in_inline():
    assert_issues('multiline_macros_in_inline', [
        MultilineMacrosInInlineError(Position(5)),
        MultilineMacrosInInlineError(Position(13)),
        MultilineMacrosInInlineError(Position(19)),
        MultilineMacrosInInlineError(Position(25)),
    ])


def test_invalid_same_name_warning():
    assert_issues('same_name_warning', [
        SameNameWarning('m1', Position(7), Position(1)),
        SameNameWarning('m2', Position(12), Position(5))
    ])


def test_special_symbols_in_name_warning():
    assert_issues('special_symbols_in_name_warning', [
        SpecialSymbolsInNameWarning('.l~0', '~', Position(3)),
        SpecialSymbolsInNameWarning('m~0', '~', Position(1)),
        SpecialSymbolsInNameWarning('.l~1', '~', Position(8)),
        SpecialSymbolsInNameWarning('m~1', '~', Position(6)),
        SpecialSymbolsInNameWarning('i~', '~', Position(12)),
        SpecialSymbolsInNameWarning('.l~1', '~', Position(18)),
        SpecialSymbolsInNameWarning('i(a~a, b~b)', '~', Position(16)),
    ])


def valid(sample_name: str):
    real_pt = preprocess(get_preproc_sample_path(f'{sample_name}/code', is_valid=True)).pt
    expected_code_path = get_preproc_sample_path(f'{sample_name}/expected', is_valid=True)

    expected_code = helpers.load_file(expected_code_path)

    assert helpers.tabs_to_spaces(PtToCode().visit(real_pt)) \
           == helpers.tabs_to_spaces(expected_code)


def test_macroinsts():
    valid('macroinsts')


def test_inline_macros():
    valid('inline_macros')


def test_macros():
    valid('macros')


def test_label_converting():
    valid('label_converting')
