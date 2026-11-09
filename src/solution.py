import sys
import pynusmv

from pynusmv.fsm import BddFsm
from pynusmv.prop import Spec
from pynusmv.dd import BDD

from helpers import *

def symbolic_reachability(model: BddFsm) -> BDD:
    """
    Compute the region of all states reachable 
    from the initial states of the FSM
    """
    
    reachable_states = model.init.intersection(model.state_constraints)
    new_reached_states = reachable_states
    
    while not new_reached_states.is_false():
        new_reached_states = model.post(new_reached_states).diff(reachable_states)
        reachable_states = reachable_states.union(new_reached_states)
    return reachable_states


def infinite_true_execution(model: BddFsm, property: BDD) -> BDD:
    """
    Compute the region of all states from which there is 
    an infinite execution where the Boolean property (varphi) 
    holds in every state along the execution
    """
    previous_states = pynusmv.dd.BDD.true()
    EG_states = property
    while not previous_states.equal(EG_states):
        previous_states = EG_states
        EG_states = model.pre(EG_states).intersection(EG_states)
    return EG_states


def check_leadsto_spec(spec: Spec) -> tuple[bool, dict]:
    """
    Return whether the loaded SMV model satisfies or not 
    the leads-to formula `spec`, that is, whether all 
    executions of the model satisfies `spec` or not.
    """
    if parse_formula(spec) is None:
        return None

    fsm = pynusmv.glob.prop_database().master.bddFsm
    reachable_states = symbolic_reachability(fsm)

    f = spec_to_bdd(fsm, parse_formula(spec)[0])
    negated_g = spec_to_bdd(fsm, parse_formula(spec)[1]).not_()

    EG_negated_g = infinite_true_execution(fsm, negated_g)
    violation_states = negated_g.intersection(fsm.pre(EG_negated_g, f))

    reachable_violations = reachable_states.intersection(violation_states)

    # TODO: Counterexample algorithm
    return (True, None) if reachable_violations.is_false() else (False, None)


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
            print("property is not LTLSPEC, skipping\n\n")
            continue
        res = check_leadsto_spec(spec)
        if res is None:
            print("Property is not a leads-to formula, skipping\n\n")
        elif res[0] is True:
            print("Property is respected\n\n")
        elif res[0] is False:
            print("Property is not respected\n\n")
            print("Counterexample:", res[1])

    pynusmv.init.deinit_nusmv()