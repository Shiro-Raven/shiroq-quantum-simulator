try:
    import cupy as np
except ModuleNotFoundError:
    try:
        import numpy as np
    except ModuleNotFoundError:
        print('Neither Cupy nor NumPy are installed')

import matplotlib.pyplot as plt

def create_state(psi, phi, theta):
    """
    This function creates an arbitrary state by taking in 
    the parameters of the Bloch sphere (theta, phi) along with the global phase (psi)
    """
    phase = np.exp(psi*1.j)

    cos = np.cos(theta / 2)
    sin = np.sin(theta / 2)

    active_phase = np.exp(phi*1.j)

    return phase * np.array([cos, active_phase * sin])

def tensor_product_vector_list(vector_list):
    if len(vector_list) > 1:
        tmp = (vector_list[0][:, None] * vector_list[1][None, :]).reshape(4,)

        for i in range(2, len(vector_list)):
            tmp = (tmp[:, None] * vector_list[i][None, :]).reshape(2 ** (i + 1),)
    else:
        tmp = vector_list[0]
    
    return tmp 

def tensor_product_matrix_list(matrix_list):
    if len(matrix_list) == 1:
        tmp = matrix_list[0]
    else:
        tmp = np.kron(matrix_list[0], matrix_list[1])

        for i in range(2, len(matrix_list)):
                tmp = np.kron(tmp, matrix_list[i])
    
    return tmp

def reorder_gate(G, circuit_length, is_big_endian, *new_targets):
    """
    This function reorders a multiqubit gate by starting with a normal up-to-down gate 
    and permuting its elements based on the order of the indices in new targets
    """

    # initialise an empty permuation list
    perm = [-1] * circuit_length

    # set the new targets at the correct indices, accounting for the endianness
    counter = 0
    for target in new_targets:
        if is_big_endian:
            idx = target
        else:
            idx = circuit_length - target - 1
        
        perm[idx] = counter
        counter += 1

    # fill in the rest of the permuation list with the remaining indices
    for _ in range(circuit_length):
        if perm[_] == -1:
            perm[_] = counter
            counter += 1

    # reorder both input and output dimensions
    perm2 = perm + [circuit_length + i for i in perm]
    
    # Do the actual permutation
    return np.reshape(np.transpose(np.reshape(G, 2*circuit_length*[2]), perm2), (2**circuit_length, 2**circuit_length))

def plot_counts(counts):
    assert isinstance(counts, dict), 'Must be a dict of counts!'
    assert len(counts.keys()) > 0, 'Dict is empty!'

    plt.bar(counts.keys(), counts.values(), 0.75, color='g')