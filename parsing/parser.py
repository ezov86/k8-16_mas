from ply import yacc
from parsing.errors import InvalidSyntaxError, UnexpectedEofError
# ply.yacc requires this import.
# noinspection PyUnresolvedReferences
from parsing.lexer import tokens
from parsing.ast import *


def list_rule(p, list_i):
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[list_i]

    return p[0]


def p_root(p):
    """ root    :
                | macroinstructions_defs
                | macros_defs macroinstructions_defs """
    if len(p) == 3:
        p[0] = Root(p[1], p[2]).set_position(Position.start())
    elif len(p) == 2:
        p[0] = Root([], p[1]).set_position(Position.start())
    else:
        p[0] = Root([], [])


def p_macros_defs(p):
    """ macros_defs : macros_def
                    | macros_def macros_defs """
    list_rule(p, 2)


def p_macros_def(p):
    """ macros_def  : inline_macros_def
                    | multiline_macros_def """
    p[0] = p[1]


def p_inline_macros_def(p):
    """ inline_macros_def : INLINE_MACROS id_with_params microinstruction """
    p[0] = MacrosDefinition(p[2][0], p[2][1], [p[3]], is_inline=True).set_position(Position.from_parser_ctx(p))


def p_multiline_macros_def(p):
    """ multiline_macros_def    : MULTILINE_MACROS id_with_params LBRACE microinstructions_with_labels RBRACE  """
    p[0] = MacrosDefinition(p[2][0], p[2][1], p[4]).set_position(Position.from_parser_ctx(p))


def p_macroinstructions_defs(p):
    """ macroinstructions_defs  : macroinstruction_def
                                | macroinstruction_def macroinstructions_defs """
    list_rule(p, 2)


def p_macroinstruction_def(p):
    """ macroinstruction_def    : MACROINSTRUCTION id_with_params LBRACE microinstructions_with_labels RBRACE """
    p[0] = MacroinstructionDefinition(p[2][0], p[2][1], p[4]).set_position(Position.from_parser_ctx(p))


def p_microinstructions_with_labels(p):
    """ microinstructions_with_labels   : microinstruction_with_label
                                        | microinstruction_with_label microinstructions_with_labels """
    list_rule(p, 2)


def p_microinstruction_with_label(p):
    """ microinstruction_with_label : microinstruction
                                    | ID COLON microinstruction """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]
        p[0].label = p[1]


def p_microinstruction(p):
    """ microinstruction    : bit_masks SEMICOLON
                            | bit_masks AT ID SEMICOLON """
    p[0] = Microinstruction(p[1]).set_position(Position.from_parser_ctx(p))

    if len(p) == 5:
        p[0].next_microinstruction_label = p[3]


def p_bit_masks(p):
    """ bit_masks   : bit_mask
                    | bit_mask PIPE bit_masks """
    list_rule(p, 3)


def p_bit_mask(p):
    """ bit_mask    : id_with_params """
    p[0] = BitMask(p[1][0], p[1][1]).set_position(Position.from_parser_ctx(p))


def p_id_with_params(p):
    """ id_with_params  : ID
                        | ID LPAR params RPAR"""
    if len(p) == 2:
        p[0] = (p[1], [])
    else:
        p[0] = (p[1], p[3])


def p_params(p):
    """ params  : ID
                | ID COMMA params """
    list_rule(p, 3)


def p_error(p):
    if p is None:
        UnexpectedEofError().handle()
    else:
        InvalidSyntaxError(p).handle()


parser = yacc.yacc()
