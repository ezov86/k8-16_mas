from context import Context
from stages.args_parsing import ArgsParsing
from stages.cpu import CpuConfigLoadingStage
from stages.parsing import CodeParsing
from stages.preproc import PreprocessingStage

if __name__ == '__main__':
    args_parsing = ArgsParsing()
    code_parsing = CodeParsing()
    cpu_config_loading = CpuConfigLoadingStage()
    preprocessing_stage = PreprocessingStage()

    args_parsing\
        .set_next(code_parsing)\
        .set_next(cpu_config_loading)\
        .set_next(preprocessing_stage)

    args_parsing.handle(Context())
