from args.stage import ArgsParsingStage
from parsing.stage import ParsingStage

if __name__ == '__main__':
    args_parsing_stage = ArgsParsingStage()
    parsing_stage = ParsingStage()

    args_parsing_stage.set_next(parsing_stage)

    args_parsing_stage.handle()
