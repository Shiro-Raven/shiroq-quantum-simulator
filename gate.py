import cupy as cp
from math import cos, sin

class QuantumGate():
    __supported_gates = ['I', 'Z', 'X', 'Y', 'H']
    
    __I = cp.eye(2, dtype='complex')

    __X = cp.array([[0., 1.], [1., 0.]], dtype='complex')
    __Z = cp.array([[1., 0.], [0., -1.]], dtype='complex')
    __Y = cp.array([[0, -1.j],[1.j, 0]], dtype='complex')
    __H = 1 / cp.sqrt(2) * cp.array([[1., 1.], [1., -1.]], dtype='complex')

    def __init__(self, *inp, controlled=False):

        assert len(inp) in [1, 2, 4], 'Invalid parameter length. Either pass the gate name, axis and the rotation parameters, or U3 and the angles'


        if len(inp) == 1:
            self.__matrix = self.__get_gate_by_name(inp[0])
        elif len(inp) == 2:
            self.__matrix = self.__calculate_axis_rotation_matrix(inp[0], inp[1]) 
        elif len(inp) == 4:
            self.__matrix = self.__calculate_arbitrary_unitary(inp[0], inp[1], inp[2], inp[3])

        if controlled:
            self.__matrix = self.__get_controlled_version(self.__matrix)

        self.__matrix = cp.around(self.__matrix, 10)
        
    def get_matrix(self):
        return self.__matrix
    
    def __get_gate_by_name(self, name):
        assert name in self.__supported_gates, 'Unsupported non-parametric Gate, supported gates are {}'.format(self.__supported_gates)

        if name == 'X':
            return self.__X
        elif name == 'Y':
            return self.__Y
        elif name == 'Z':
            return self.__Z
        elif name == 'I':
            return self.__I
        elif name == 'H':
            return self.__H

    def __calculate_axis_rotation_matrix(self, axis, theta):
        assert  axis in ['Rx', 'Ry', 'Rz'], 'Invalid axis choice. Can only be [\'Rx\', \'Ry\', \'Rz\']'
        assert cp.isreal(theta), 'Theta can not be complex'

        axis = axis[-1]

        if axis in ['x', 'y']:
            cosTheta = cos(theta / 2)
            sinTheta = sin(theta / 2)

            if axis == 'x':
                return cp.array([[cosTheta, -1.j*sinTheta],[-1.j*sinTheta, cosTheta]], dtype='complex')
            else:
                return cp.array([[cosTheta, -sinTheta],[sinTheta, cosTheta]], dtype='complex')
        else:
            return cp.array([[cp.exp(-1.j*theta / 2), 0],[0, cp.exp(1.j*theta / 2)]], dtype='complex')


    def __calculate_arbitrary_unitary(self, name, theta, phi, lamda):
        assert name == 'U3', 'Wrong gate name. should be U3'
        assert cp.isreal(theta), 'Theta is not real'
        assert cp.isreal(phi), 'Phi is not real'
        assert cp.isreal(lamda), 'Lambda is not real'

        cosTheta = cos(theta / 2)
        sinTheta = sin(theta / 2)
        exp_phi = cp.exp(1.j*phi)
        exp_lambda = cp.exp(1.j*lamda)

        return cp.array([[cosTheta, -exp_lambda*sinTheta],[exp_phi*sinTheta, exp_lambda*exp_phi*cosTheta]], dtype='complex')

    def __get_controlled_version(self, gate):
        res = cp.identity(4, dtype=complex)

        res[2:4, 2:4] = gate

        return res 