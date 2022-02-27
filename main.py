from context import Context
from stages.args_parsing import ArgsParsing
from stages.cpu import CpuConfigLoading
from stages.code_parsing import CodeParsing
from stages.preproc import Preprocessing

if __name__ == '__main__':
    args_parsing = ArgsParsing()
    code_parsing = CodeParsing()
    cpu_config_loading = CpuConfigLoading()
    preproc = Preprocessing()

    args_parsing\
        .set_next(code_parsing)\
        .set_next(cpu_config_loading)\
        .set_next(preproc)\

    args_parsing.handle(Context())
