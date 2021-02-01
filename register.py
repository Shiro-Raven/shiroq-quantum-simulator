import cupy as cp
from gate import QuantumGate
import utils
import math

import warnings

class QuantumRegister():
    # Have a set of common states
    zero = cp.array([1., 0.], dtype='complex')
    one = cp.array([0.,1.], dtype='complex')
    plus = cp.array([1/cp.sqrt(2), 1/cp.sqrt(2)], dtype='complex')
    minus = cp.array([1/cp.sqrt(2), -1/cp.sqrt(2)], dtype='complex')

    __one_test = cp.array(1.)

    def __init__(self, size, endianness='big'):
        assert size < 26, 'Maximum allowed qubits is 25'
        assert size > 0, 'Can not have empty register'

        self.set_endianness(endianness)
        self.__size = size

        self.reset()

    def reset(self):
        # Needed for efficiency purposes
        self.__dirty = True
        self.__unapplied_gates = False
        self.__opmatrix_calculated = False

        # Needed for correctness
        self.__initialised = False

        # initialise all states to zero
        self.__qubits = cp.stack([self.zero] * self.__size, axis = 0)

        self.__gate_cache = cp.tile(cp.eye(2, dtype='complex'), (self.__size, 1)).reshape(-1, 2, 2)
        self.__operators_matrix = cp.eye(2 ** self.__size)


    def get_register_size(self):
        return self.__size

    def set_endianness(self, endianness):
        assert endianness in ['big', 'little'], 'Endianness can only be big or little'
        self.__is_big_endian = endianness == 'big'

    def get_endianness(self):
        return 'big' if self.__is_big_endian else 'little'

    def run_program(self, program):
        assert isinstance(program, list), 'Program must be a list'
        
        for instruction in program:
            params = instruction[:-1]
            
            gate = QuantumGate(*params)

            self.add_gate(gate, instruction[-1])

        self.apply()

    def __appropriate_index(self, index):
        return index if self.__is_big_endian else self.__size - index - 1

    def initialise_qubit(self, index, state):
        assert not self.__initialised, 'Can not set states after adding a gate'
        assert index < self.__size, 'Qubit not in register'
        cp.testing.assert_array_equal(cp.around(cp.sum(cp.absolute(state) ** 2)), self.__one_test, 'Non-quantum mechanical state', False)

        index = self.__appropriate_index(index)

        self.__dirty = True 
        self.__qubits[index] = state

    def get_statevector(self):
        if self.__dirty:
            # TODO: if time allows, make this more efficient
            self.__statevector = utils.tensor_product_vector_list(self.__qubits)

        self.__dirty = False

        return self.__statevector

    def add_gate(self, gate, targets):
        self.__do_assertions(gate, targets)

        gate = gate.get_matrix()

        #breakpoint()

        for i in range(len(targets)):
            targets[i] =  self.__appropriate_index(targets[i])

        #breakpoint()

        affected_qubits = int(math.log(gate.shape[0], 2))
        ############################################
        if affected_qubits == 1:
            for target in targets:
                target = self.__appropriate_index(target)
                self.__gate_cache[target] = gate @ self.__gate_cache[target]
            self.__opmatrix_calculated = False
        else:
            if self.__size > affected_qubits:
                tmp = cp.tile(cp.eye(2, dtype='complex'), (self.__size - affected_qubits, 1)).reshape(-1, 2, 2)
                tmp = utils.tensor_product_matrix_list(tmp)
                tmp = cp.kron(gate, tmp)
            else:
                tmp = gate

            gate = utils.reorder_gate(tmp, self.__size, self.__is_big_endian, *targets)

            ops_matrix = self.__calculate_operators_product()

            self.__operators_matrix = gate @ ops_matrix
        ############################################

        self.__unapplied_gates = True
        self.__initialised = True

    def __do_assertions(self, gate, targets):
        assert all([target < self.__size for target in targets]), 'Some qubits not in register'
        assert len(targets) == len(set(targets)), 'All target qubits must be different!'
        
        affected_qubits = int(math.log(gate.get_matrix().shape[0], 2))
        assert affected_qubits <= self.__size, 'Gate too big for circuit'
        
        if affected_qubits > 1:
            assert affected_qubits == len(targets), 'Too many/too few arguments for target qubits'

    def __calculate_operators_product(self):
        if not self.__opmatrix_calculated:
            tmp = utils.tensor_product_matrix_list(self.__gate_cache)
            self.__operators_matrix = tmp @ self.__operators_matrix 
            self.__gate_cache = cp.tile(cp.eye(2, dtype='complex'), (self.__size, 1)).reshape(-1, 2, 2)

        self.__opmatrix_calculated = True

        return self.__operators_matrix

    def apply(self):
        if not self.__unapplied_gates:
            return
        self.__unapplied_gates = False

        statevector = self.get_statevector()
        operators_matrix = self.__calculate_operators_product()

        self.__statevector = operators_matrix @ statevector

        self.__operators_matrix = cp.eye(2 ** self.__size)

    def measure(self, shots, qubits_idx=None):
        assert qubits_idx is None or isinstance(qubits_idx, list), 'Incorrect way of indexing qubits'
        if qubits_idx == None:
            qubits_idx = [self.__appropriate_index(i) for i in range(self.__size)]
        assert max(qubits_idx) < self.__size or min(qubits_idx) >= 0, 'Some qubits not in register'

        if self.__unapplied_gates:
            warnings.warn('Some gates are not applied yet! Call QuantumRegister.apply()')

        statevector = self.get_statevector()
        values, counts = cp.unique(cp.random.choice(len(statevector), shots, p=cp.absolute(statevector) ** 2), return_counts=True)
        values = list(cp.asnumpy(values))
        values = [format(i, '0' + str(self.__size) + 'b') for i in values]
        
        # TODO make this more efficient
        res = dict()
        for i, value in enumerate(values):
            key = ''.join([value[i] for i in qubits_idx])
            if key in res.keys():
                res[key] += counts[i].item()
            else:
                res[key] = counts[i].item()
        return res