import pynusmv

def verify_region(model, varphi):
    z_old = pynusmv.dd.BDD.true()
    z = varphi
    while not z_old.equal(z):
        z_old = z
        z = model.pre(z).intersection(z)
    return z


