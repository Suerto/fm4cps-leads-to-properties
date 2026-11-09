import pynusmv

from pynusmv_lower_interface.nusmv.parser import parser
from pynusmv.fsm import BddFsm
from pynusmv.prop import Spec
from pynusmv.dd import BDD

SPEC_TYPES = {
    "LTLSPEC": parser.TOK_LTLSPEC,
    "CONTEXT": parser.CONTEXT,
    "IMPLIES": parser.IMPLIES,
    "IFF": parser.IFF,
    "OR": parser.OR,
    "XOR": parser.XOR,
    "XNOR": parser.XNOR,
    "AND": parser.AND,
    "NOT": parser.NOT,
    "ATOM": parser.ATOM,
    "NUMBER": parser.NUMBER,
    "DOT": parser.DOT,
    "NEXT": parser.OP_NEXT,
    "OP_GLOBAL": parser.OP_GLOBAL,
    "OP_FUTURE": parser.OP_FUTURE,
    "UNTIL": parser.UNTIL,
    "EQUAL": parser.EQUAL,
    "NOTEQUAL": parser.NOTEQUAL,
    "LT": parser.LT,
    "GT": parser.GT,
    "LE": parser.LE,
    "GE": parser.GE,
    "TRUE": parser.TRUEEXP,
    "FALSE": parser.FALSEEXP,
}

BASIC_TYPES = {
    parser.ATOM,
    parser.NUMBER,
    parser.TRUEEXP,
    parser.FALSEEXP,
    parser.DOT,
    parser.EQUAL,
    parser.NOTEQUAL,
    parser.LT,
    parser.GT,
    parser.LE,
    parser.GE,
}

BOOLEAN_OP = {
    parser.AND,
    parser.OR,
    parser.XOR,
    parser.XNOR,
    parser.IMPLIES,
    parser.IFF,
}


def spec_to_bdd(model: BddFsm, spec: Spec) -> BDD:
    """
    Given a formula `spec` with no temporal operators, returns a BDD equivalent to
    the formula, that is, a BDD that contains all the states of `model` that
    satisfy `spec`
    """
    bddspec = pynusmv.mc.eval_simple_expression(model, str(spec))
    return bddspec


def is_boolean_formula(spec: Spec) -> bool:
    """
    Given a formula `spec`, checks if the formula is a boolean combination of base
    formulas with no temporal operators.
    """
    if spec.type in BASIC_TYPES:
        return True
    if spec.type == SPEC_TYPES["NOT"]:
        return is_boolean_formula(spec.car)
    if spec.type in BOOLEAN_OP:
        return is_boolean_formula(spec.car) and is_boolean_formula(spec.cdr)
    return False


def parse_formula(spec: Spec) -> tuple[Spec, Spec]:
    """
    Visit the syntactic tree of the formula `spec` to check if it is a leads-to formula,
    that is wether the formula is of the form

                    G (f -> F g)

    where f and g are boolean combination of basic formulas.

    If `spec` is a leads-to formula, the result is a pair where the first element is the
    formula f and the second element is the formula g. If `spec` is not a leads-to
    formula, then the result is None.
    """
    # the root of a spec should be of type CONTEXT
    if spec.type != SPEC_TYPES["CONTEXT"]:
        return None
    # the right child of a context is the main formula
    spec = spec.cdr
    # the root of a leads-to formula should be of type OP_GLOBAL
    if spec.type != SPEC_TYPES["OP_GLOBAL"]:
        return None
    # The formula in the scope of the G operator must be of type IMPLIES
    spec = spec.car
    if spec.type != SPEC_TYPES["IMPLIES"]:
        return None
    # Check if lhs of the implication is a formula with no temporal operators
    f_formula = spec.car
    if not is_boolean_formula(f_formula):
        return None
    # Check if rhs of the implication is a F g formula
    g_formula = spec.cdr
    if g_formula.type != SPEC_TYPES["OP_FUTURE"]:
        return None
    g_formula = g_formula.car
    if not is_boolean_formula(g_formula):
        return None
    return (f_formula, g_formula)
