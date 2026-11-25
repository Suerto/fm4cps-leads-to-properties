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
    EG_states = property.intersection(model.state_constraints)
    while not previous_states.equal(EG_states):
        previous_states = EG_states
        EG_states = model.pre(EG_states).intersection(EG_states)
    return EG_states

def check_leadsto_spec(spec: Spec) -> tuple[bool, dict]:
    """
    Returns wheter the loaded SMV model satisfies or not
    the leads-to formula `spec`, that is, whether all
    executions of the model satisfies `spec` or not.
    """

    # If spec is not an LTL-Formula, return immediately
    parsed = parse_formula(spec)
    if parsed is None:
        return None

    fsm = pynusmv.glob.prop_database().master.bddFsm
    


#def check_leadsto_spec(spec: Spec) -> tuple[bool, dict]:
#    """
#    Return whether the loaded SMV model satisfies or not 
#    the leads-to formula `spec`, that is, whether all 
#    executions of the model satisfies `spec` or not.
#    """
#    parsed = parse_formula(spec)
#    if parsed is None:
#        return None
#
#    fsm = pynusmv.glob.prop_database().master.bddFsm
#
#    f = spec_to_bdd(fsm, parse_formula(spec)[0])
#    negated_g = spec_to_bdd(fsm, parse_formula(spec)[1]).not_()
#
#    EG_negated_g = infinite_true_execution(fsm, negated_g)
#    violation_states = negated_g.intersection(fsm.pre(EG_negated_g, f))
#
#    reachable_states = symbolic_reachability(fsm)
#    reachable_violations = reachable_states.intersection(violation_states)
#
#    if reachable_violations.is_false():
#        return (True, None)
#
#    # Counterexample Algorithm
#    layers = []
#    current = fsm.init.intersection(fsm.state_constraints)
#    visited = current
#    layers.append(current)
#
#    while current.intersection(violation_states).is_false():
#        current = fsm.post(current).diff(visited)
#        visited = visited.union(current)
#        layers.append(current)
#
#    violation_start = fsm.pick_one_state(layers[-1].intersection(violation_states))
#    current_state = violation_start
#    prefix = [current_state.get_str_values()]
#
#    for layer in reversed(layers[:-1]):
#        predecessors = fsm.pre(current_state).intersection(layer)
#        previous_state = fsm.pick_one_state(predecessors)
#        input_state = fsm.pick_one_inputs(fsm.get_inputs_between_states(previous_state, current_state))
#
#        prefix.append(input_state.get_str_values())
#        prefix.append(previous_state.get_str_values())
#        current_state = previous_state
#    prefix.reverse()
#    trace = list(prefix)
#
#    next_candidates = fsm.post(violation_start, f).intersection(EG_negated_g)
#    next_state = fsm.pick_one_state(next_candidates)
#    first_input = fsm.pick_one_inputs(fsm.get_inputs_between_states(violation_start, next_state).intersection(f))
#
#    trace.append(first_input.get_str_values())
#    trace.append(next_state.get_str_values())
#
#    if next_state.equal(violation_start):
#        return (False, tuple(trace))
#
#    visited_suffix_states = [violation_start, next_state]
#    curr_suffix = next_state
#
#    while True:
#        succ_candidates = (
#            fsm.post(curr_suffix)
#            .intersection(EG_negated_g)
#            .intersection(fsm.state_constraints)
#        )
#        next_state = fsm.pick_one_state(succ_candidates)
#        step_input = fsm.pick_one_inputs(
#            fsm.get_inputs_between_states(curr_suffix, next_state)
#        )
#
#        trace.append(step_input.get_str_values())
#        trace.append(next_state.get_str_values())
#
#        if any(next_state.equal(s) for s in visited_suffix_states):
#            break
#
#        visited_suffix_states.append(next_state)
#        curr_suffix = next_state
#
#    return (False, tuple(trace))

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