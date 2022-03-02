import argparse

from context import Context
from stage import Stage


class ArgsParsing(Stage):
    def handle(self, context: Context):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('source_file_path', help='Путь к файлу с исходным кодом.')
        arg_parser.add_argument('-p', '--stop-after-parsing',
                                help='Остановиться после парсинга и вывести AST в формате JSON.',
                                action='store_true', default=False)
        arg_parser.add_argument('-w', '--ignore-warnings', help='Игнорировать предупреждения.',
                                action='store_true', default=False)
        arg_parser.add_argument('-c', '--use-csv', help='Выводить микропрограмму в формате CSV.',
                                action='store_true', default=False)
        arg_parser.add_argument('-i', '--use-intel-hex', help='Выводить программу в формате Intel-HEX.',
                                action='store_true', default=False)
        arg_parser.add_argument('--cpu-config-path', help='Указать путь к конфигурации процессора.',
                                action='store', default='default_cpu_config.json')
        arg_parser.add_argument('-r', '--stop-after-preprocessing', help='Остановиться после работы препроцессора и '
                                                                         'вывести обработанное дерево в формате JSON.',
                                action='store_true', default=False)
        arg_parser.add_argument('-o', '--output-file-path', help='Указать путь к выходному файлу.', action='store',
                                default='out')
        arg_parser.add_argument('-g', '--generator', help='Название генератора выходных данных (bin|csv).',
                                action='store', default='bin')

        args = arg_parser.parse_args()

        context.args.source_file_path = args.source_file_path
        context.args.stop_after_parsing = args.stop_after_parsing
        context.args.ignore_warnings = args.ignore_warnings
        context.args.use_csv = args.use_csv
        context.args.use_intel_hex = args.use_intel_hex
        context.args.cpu_config_path = args.cpu_config_path
        context.args.stop_after_preprocessing = args.stop_after_preprocessing
        context.args.output_file_path = args.output_file_path
        context.args.generator = args.generator

        return super().handle(context)
