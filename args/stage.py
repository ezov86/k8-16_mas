import argparse

from args.manager import ArgsManager
from base_stage import BaseStage


class ArgsParsingStage(BaseStage):
    def handle(self, _=None):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('source_file_path', help='Source code file path.')
        arg_parser.add_argument('-p', '--stop-after-parsing',
                                help='Stop after parsing and dump AST in JSON format.',
                                action='store_true')
        arg_parser.add_argument('-w', '--ignore-warnings', help='Ignore warning messages.',
                                action='store_true')
        arg_parser.add_argument('-c', '--use-csv', help='Use CSV as output format.',
                                action='store_true')
        arg_parser.add_argument('-i', '--use-intel-hex', help='Use Intel HEX as output format.',
                                action='store_true')

        ArgsManager().init(arg_parser.parse_args())

        super().handle(ArgsManager().source_file_path)
