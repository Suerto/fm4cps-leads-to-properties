import pynusmv

def infinitely_true(model: pynusmv.fsm.BddFsm, property: pynusmv.dd.BDD) -> pynusmv.dd.BDD:
    """
    Compute the region of all states from which there is an 
    infinite execution where the Boolean property (varphi) holds in every state along the execution
    """
    previous_states = pynusmv.dd.BDD.true()
    EG_states = property
    while not previous_states.equal(EG_states):
        previous_states = EG_states
        EG_states = model.pre(EG_states).intersection(EG_states)
    return EG_states