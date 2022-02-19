import json
from typing import List

from args.manager import ArgsManager
from base_stage import BaseStage
from parsing.ast import Root, MacroinstDef
from preproc.ast_to_pt import AstToPt
from preproc.pt_to_code import PtToCodeVisitor


class PreprocessingStage(BaseStage):
    def handle(self, ast: Root) -> List[MacroinstDef]:
        pt = AstToPt().visit(ast)

        if ArgsManager.stop_after_preprocessing:
            print(PtToCodeVisitor(tracking=True).visit(pt))
            super().handle_issues()
            exit(0)

        super().handle_issues()

        return super().handle(pt)
