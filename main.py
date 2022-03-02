from context import Context
from stages.args_parsing import ArgsParsing
from stages.codegen import CodeGeneration
from stages.cpu import CpuConfigLoading
from stages.code_parsing import CodeParsing
from stages.preproc import Preprocessing

if __name__ == '__main__':
    args_parsing = ArgsParsing()
    code_parsing = CodeParsing()
    cpu_config_loading = CpuConfigLoading()
    preproc = Preprocessing()
    codegen = CodeGeneration()

    args_parsing\
        .set_next(code_parsing)\
        .set_next(cpu_config_loading)\
        .set_next(preproc)\
        .set_next(codegen)

    args_parsing.handle(Context())
