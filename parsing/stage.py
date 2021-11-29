import json

from args.manager import ArgsManager
from base_stage import BaseStage
from parsing.parser import parser
from parsing.ast_to_dict_visitor import AstToDictVisitor


class ParsingStage(BaseStage):
    def handle(self, source_file_path: str):
        with open(source_file_path) as file:
            text = file.read()

        ast = parser.parse(text, tracking=True)

        self.handle_issues()

        if ArgsManager().stop_after_parsing:
            ast_dict = AstToDictVisitor().visit(ast)
            print(json.dumps(ast_dict))
            exit(0)

        super().handle(ast)
