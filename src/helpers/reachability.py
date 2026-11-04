import pynusmv

def reachable_states(model):
    """
    Compute the region of all states reachable from the initial states
    """
    reachable_states = model.init
    new_reached_states = reachable_states

    while not new_reached_states.is_false():
        new_reached_states = model.post(new_reached_states).diff(reachable_states)
        reachable_states = reachable_states.union(new_reached_states)
    return reachable_states