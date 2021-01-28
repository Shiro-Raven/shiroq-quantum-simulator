import cupy as cp

def create_state(psi, phi, theta):
    phase = cp.exp(psi*1.j)

    cos = cp.cos(theta / 2)
    sin = cp.sin(theta / 2)

    active_phase = cp.exp(phi*1.j)

    return phase * cp.array([cos, active_phase * sin])