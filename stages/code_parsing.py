import json

from ply import yacc, lex

from assembler_ast import *
from visitors.ast_to_dict import AstToDict
from context import Context
from issue import AssemblyError
from position import Position
from stage import Stage


class CodeParsing(Stage):
    def handle(self, context: Context):
        with open(context.args.source_file_path) as file:
            text = file.read()

        context.ast = Parser(context).parse(text, tracking=True)

        if context.args.stop_after_parsing:
            ast_dict = AstToDict(tracking=True).visit(context.ast)
            print(json.dumps(ast_dict))
            super().check_for_issues(context)
            exit(0)

        return super().handle(context)


class LexerError(AssemblyError):
    def __init__(self, token):
        self.token = token.value
        super().__init__(f'неверный токен "{token.value}"', Position.from_lex_token(token))


class InvalidSyntaxError(AssemblyError):
    def __init__(self, p):
        self.p = p.value
        super().__init__(f'неверный синтаксис в "{p.value}"', Position.from_parser_token(p))


class UnexpectedEofError(AssemblyError):
    def __init__(self):
        super().__init__('неожиданный конец файла')


class Parser:
    def __init__(self, context: Context):
        self.lex = lex.lex(module=self)
        self.yacc = yacc.yacc(module=self)
        self.context = context

    def parse(self, text: str, tracking=True) -> any:
        return self.yacc.parse(input=text, tracking=tracking)

    # Лексер
    tokens = (
        'ID',
        'PIPE',
        'SEMICOLON',
        'LPAR',
        'RPAR',
        'COMMA',
        'LBRACE',
        'RBRACE',
        'MULTILINE_MACROS',
        'INLINE_MACROS',
        'MACROINSTRUCTION',
        'AT',
        'COLON'
    )

    t_PIPE = r'\|'
    t_SEMICOLON = r'\;'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_COMMA = r'\,'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_MULTILINE_MACROS = r'\%m'
    t_INLINE_MACROS = r'\%mi'
    t_MACROINSTRUCTION = r'\%i'
    t_AT = r'@'
    t_COLON = r':'

    def t_NEWLINE(self, t):
        r"""\n"""
        t.lexer.lineno += 1

    def t_COMMENT(self, t):
        r"""\#[^\n\r]*"""
        t.lexer.lineno += t.value.count('\n')

    def t_ID(self, t):
        r"""[^\s|;(),%{}@:]+"""
        return t

    t_ignore = '\t \r'

    def t_error(self, t):
        self.context.handle_issue(LexerError(t))
        t.lexer.skip(1)

    # Парсер
    def list_rule(self, p, list_i):
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[list_i]

        return p[0]

    def get_name_with_params(self, name: str, params: List[str]) -> str:
        return f'{name}({", ".join(params)})'

    def p_root(self, p):
        """ root    :
                    | macroinstructions_defs
                    | macros_defs macroinstructions_defs """
        if len(p) == 3:
            p[0] = Root(p[1], p[2])
        elif len(p) == 2:
            p[0] = Root([], p[1])
        else:
            p[0] = Root([], [])

    def p_macros_defs(self, p):
        """ macros_defs : macros_def
                        | macros_def macros_defs """
        self.list_rule(p, 2)

    def p_macros_def(self, p):
        """ macros_def  : inline_macros_def
                        | multiline_macros_def """
        p[0] = p[1]

    def p_inline_macros_def(self, p):
        """ inline_macros_def : INLINE_MACROS id_with_params microinstruction SEMICOLON """
        p[0] = MacrosDef(p[2], [p[3]], is_inline=True)
        p[0].position = Position.from_parser_ctx(p)

    def p_multiline_macros_def(self, p):
        """ multiline_macros_def    : MULTILINE_MACROS id_with_params LBRACE microinstructions_with_labels RBRACE  """
        p[0] = MacrosDef(p[2], p[4])
        p[0].position = Position.from_parser_ctx(p)

    def p_macroinstructions_defs(self, p):
        """ macroinstructions_defs  : macroinstruction_def
                                    | macroinstruction_def macroinstructions_defs """
        self.list_rule(p, 2)

    def p_macroinstruction_def(self, p):
        """ macroinstruction_def    : MACROINSTRUCTION id_with_params LBRACE microinstructions_with_labels RBRACE """
        p[0] = MacroinstDef(p[2], p[4])
        p[0].position = Position.from_parser_ctx(p)

    def p_microinstructions_with_labels(self, p):
        """ microinstructions_with_labels   : microinstruction_with_label
                                            | microinstruction_with_label microinstructions_with_labels """
        self.list_rule(p, 2)

    def p_microinstruction_with_label(self, p):
        """ microinstruction_with_label : microinstruction_with_next_label
                                        | ID COLON microinstruction_with_next_label """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[3]
            p[0].label_def = p[1]

    def p_microinstruction_with_next_label(self, p):
        """ microinstruction_with_next_label    : microinstruction SEMICOLON
                                                | microinstruction AT ID SEMICOLON """
        p[0] = p[1]

        if len(p) == 5:
            p[0].next_microinst_label = Label(p[3])
            p[0].next_microinst_label.position = Position.from_parser_ctx(p)

    def p_microinstruction(self, p):
        """ microinstruction    : bit_masks """
        p[0] = Microinst(p[1])
        p[0].position = Position.from_parser_ctx(p)

    def p_bit_masks(self, p):
        """ bit_masks   : bit_mask
                        | bit_mask PIPE bit_masks """
        self.list_rule(p, 3)

    def p_bit_mask(self, p):
        """ bit_mask    : id_with_params """
        p[0] = BitMask(p[1])
        p[0].position = Position.from_parser_ctx(p)

    def p_id_with_params(self, p):
        """ id_with_params  : ID
                            | ID LPAR params RPAR"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = self.get_name_with_params(p[1], p[3])

    def p_params(self, p):
        """ params  : ID
                    | ID COMMA params """
        self.list_rule(p, 3)

    def p_error(self, p):
        if p is None:
            self.context.handle_issue(UnexpectedEofError())
        else:
            self.context.handle_issue(InvalidSyntaxError(p))
