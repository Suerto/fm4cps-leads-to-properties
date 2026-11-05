import pynusmv

def reachable_states(model: pynusmv.fsm.BddFsm) -> pynusmv.dd.BDD:
    """
    Compute the region of all states reachable from the initial states of the FSM
    """
    
    reachable_states = model.init.intersection(model.state_constraints)
    new_reached_states = reachable_states
    
    while not new_reached_states.is_false():
        new_reached_states = model.post(new_reached_states).diff(reachable_states)
        reachable_states = reachable_states.union(new_reached_states)
    return reachable_states