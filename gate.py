try:
    import cupy as np
except ModuleNotFoundError:
    try:
        import numpy as np
    except ModuleNotFoundError:
        print('Neither Cupy nor NumPy are installed')

from math import cos, sin, pi

class QuantumGate():
    __supported_gates = ['i', 'z', 'x', 'y', 'h', 'swap', 'cx', 's', 't']

    __X = np.array([[0., 1.], [1., 0.]], dtype='complex')
    __Z = np.array([[1., 0.], [0., -1.]], dtype='complex')
    __Y = np.array([[0, -1.j],[1.j, 0]], dtype='complex')

    __H = 1 / np.sqrt(2) * np.array([[1., 1.], [1., -1.]], dtype='complex')
    __SWAP = np.array([[1,0,0,0], [0,0,1,0], [0,1,0,0], [0,0,0,1]], dtype='complex')

    def __init__(self, *inp):
        assert len(inp) in [1, 2, 4], 'Invalid parameter length. Either pass the gate name, axis and the rotation parameters, or U3 and the angles'

        gate_name = inp[0].lower()

        self.name = gate_name
        self.params = None

        controlled = True if gate_name[0] == 'c' else False
        gate_name = gate_name[1:] if gate_name[0] == 'c' else gate_name
        
        if len(inp) == 1:
            # Non-parametric gates
            self.__matrix = self.__get_gate_by_name(gate_name)
            self.params = None
        elif len(inp) == 2:
            # Rx, Ry, and Rz gates, as well as the phase gate
            self.__matrix = self.__calculate_axis_rotation_matrix(gate_name, inp[1]) 
        elif len(inp) == 4:
            # U3 gate
            self.__matrix = self.__calculate_arbitrary_unitary(gate_name, inp[1], inp[2], inp[3])

        # If a controlled gate is needed, generate the controlled matrix
        if controlled:
            self.__matrix = self.__get_controlled_version()

        self.__matrix = np.around(self.__matrix, 10)

    def is_single_qubit(self):
        return self.__matrix.shape[0] == 2

    def is_two_qubits(self):
        return self.__matrix.shape[0] == 4

    def get_matrix(self):
        return self.__matrix
    
    def __get_gate_by_name(self, name):
        assert name in self.__supported_gates, 'Unsupported non-parametric Gate {}, supported gates are {}'.format(name, self.__supported_gates)

        if name == 'x':
            return self.__X
        elif name == 'y':
            return self.__Y
        elif name == 'z':
            return self.__calculate_axis_rotation_matrix('u1', pi)
        elif name == 'i':
            return self.__calculate_axis_rotation_matrix('u1', 0)
        elif name == 's':
            return self.__calculate_axis_rotation_matrix('u1', pi / 2)
        elif name == 't':
            return self.__calculate_axis_rotation_matrix('u1', pi / 4)
        elif name == 'h':
            return self.__H
        elif name == 'swap':
            return self.__SWAP
        elif name == 'cx':
            self.__matrix = self.__X
            return self.__get_controlled_version()

    def __calculate_axis_rotation_matrix(self, axis, theta):
        assert axis in ['rx', 'ry', 'rz', 'u1'], 'Invalid axis choice. Can only be [\'Rx\', \'Ry\', \'Rz\', \'U1\']'
        assert np.isreal(theta), 'Theta can not be complex'

        axis = axis[-1]

        self.params = [theta]

        # Textbook definition of the matrices
        if axis in ['x', 'y']:
            cosTheta = cos(theta / 2)
            sinTheta = sin(theta / 2)

            if axis == 'x':
                return np.array([[cosTheta, -1.j*sinTheta],[-1.j*sinTheta, cosTheta]], dtype='complex')
            else:
                return np.array([[cosTheta, -sinTheta],[sinTheta, cosTheta]], dtype='complex')
        elif axis == 'z':
            return np.array([[np.exp(-1.j*theta / 2), 0],[0, np.exp(1.j*theta / 2)]], dtype='complex')
        else:
            return np.array([[1, 0],[0, np.exp(1.j*theta)]], dtype='complex')


    def __calculate_arbitrary_unitary(self, name, theta, phi, lamda):
        assert name == 'u3', 'Wrong gate name. should be U3'
        assert np.isreal(theta), 'Theta is not real'
        assert np.isreal(phi), 'Phi is not real'
        assert np.isreal(lamda), 'Lambda is not real'

        cosTheta = cos(theta / 2)
        sinTheta = sin(theta / 2)
        exp_phi = np.exp(1.j*phi)
        exp_lambda = np.exp(1.j*lamda)

        self.params = [theta, phi, lamda]

        return np.array([[cosTheta, -exp_lambda*sinTheta],[exp_phi*sinTheta, exp_lambda*exp_phi*cosTheta]], dtype='complex')

    def __get_controlled_version(self):
        if self.is_single_qubit():
            res = np.identity(4, dtype=complex)
            res[2:4, 2:4] = self.get_matrix()
        elif self.is_two_qubits():
            res = np.identity(8, dtype=complex)
            res[4:8, 4:8] = self.get_matrix()

        return res 