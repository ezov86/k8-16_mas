from args.stage import ArgsParsingStage
from cpu.stage import CpuConfigLoadingStage
from parsing.stage import ParsingStage
from preproc.stage import PreprocessingStage

if __name__ == '__main__':
    args_parsing = ArgsParsingStage()
    parsing = ParsingStage()
    cpu_config_loading = CpuConfigLoadingStage()
    preprocessing_stage = PreprocessingStage()

    args_parsing\
        .set_next(parsing)\
        .set_next(cpu_config_loading)\
        .set_next(preprocessing_stage)

    args_parsing.handle()
