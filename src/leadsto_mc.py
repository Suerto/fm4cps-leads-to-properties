import sys
import pynusmv
from pynusmv_lower_interface.nusmv.parser import parser

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


def spec_to_bdd(model, spec):
    """
    Given a formula `spec` with no temporal operators, returns a BDD equivalent to
    the formula, that is, a BDD that contains all the states of `model` that
    satisfy `spec`
    """
    bddspec = pynusmv.mc.eval_simple_expression(model, str(spec))
    return bddspec


def is_boolean_formula(spec):
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


def parse_formula(spec):
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


def check_leadsto_spec(spec):
    """
    Return whether the loaded SMV model satisfies or not the leads-to formula
    `spec`, that is, whether all executions of the model satisfies `spec`
    or not.
    """
    if parse_formula(spec) is None:
        return None

    # In order to access the BDD of the model, I use
    model = pynusmv.glob.prop_database().master.bddFsm
    print(f"Initial states of the BDD: {model.count_states(model.init)}")
    for state in model.pick_all_states(model.init):
        print(state.get_str_values())


    return [True, None]
    # return pynusmv.mc.check_explain_ltl_spec(spec)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "filename.smv")
        sys.exit(1)

    pynusmv.init.init_nusmv()
    filename = sys.argv[1]
    pynusmv.glob.load_from_file(filename)
    pynusmv.glob.compute_model()
    type_ltl = pynusmv.prop.propTypes["LTL"]
    for prop in pynusmv.glob.prop_database():
        spec = prop.expr
        print(spec)
        if prop.type != type_ltl:
            print("property is not LTLSPEC, skipping")
            continue
        res = check_leadsto_spec(spec)
        if res is None:
            print("Property is not a leads-to formula, skipping")
        elif res[0] is True:
            print("Property is respected")
        elif res[0] is False:
            print("Property is not respected")
            print("Counterexample:", res[1])

    pynusmv.init.deinit_nusmv()
