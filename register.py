import cupy as cp
from gate import QuantumGate
import utils

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

        # Needed for efficiency purposes
        self.__dirty = True
        self.__unapplied_gates = False
        self.__opmatrix_calculated = False

        # Needed for correctness
        self.__initialised = False

        # initialise all states to zero
        self.__qubits = cp.stack([self.zero] * size, axis = 0)

        self.__gate_cache = cp.tile(cp.eye(2, dtype='complex'), (self.__size, 1)).reshape(-1, 2, 2)
        self.__operators_matrix = cp.eye(2 ** size)

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

            if gate.is_single_qubit():
                target = instruction[-1]
                self.add_single_qubit_gate(gate, target)
            elif gate.is_two_qubits():
                control, target = instruction[-1]
                self.add_two_qubit_gate(gate, control, target)
            else:
                one, two, three = instruction[-1]
                self.add_three_qubit_gate(gate, one, two, three)
        
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


    def add_single_qubit_gate(self, gate, targets):
        assert max(targets) < self.__size or min(targets) >= 0, 'Some qubits not in register'

        gate = gate.get_matrix()

        for target in targets:
            target = self.__appropriate_index(target)
            self.__gate_cache[target] = gate @ self.__gate_cache[target] 

        self.__unapplied_gates = True
        self.__opmatrix_calculated = False
        self.__initialised = True


    def add_two_qubit_gate(self, gate, control, target):
        assert self.__size > 1, 'Can not have controlled gate in one qubit system'
        assert target < self.__size, 'Target qubit not in register'
        assert control < self.__size, 'Control qubit not in register'
        assert control != target, 'control and target must be different'

        gate = gate.get_matrix()

        if self.__size > 2:
            tmp = cp.tile(cp.eye(2, dtype='complex'), (self.__size - 2, 1)).reshape(-1, 2, 2)
            tmp = utils.tensor_product_matrix_list(tmp)
            tmp = cp.kron(gate, tmp)
        else: 
            tmp = gate

        control = self.__appropriate_index(control)
        target = self.__appropriate_index(target)

        gate = utils.reorder_gate(tmp, control, target, self.__size)
        
        ops_matrix = self.__calculate_operators_product()

        self.__operators_matrix = gate @ ops_matrix

        self.__unapplied_gates = True
        self.__initialised = True

    def add_three_qubit_gate(self, gate, one, two, three):
        assert self.__size > 2, 'Can not have three-qubit gate in one/two qubit system'
        assert one < self.__size, 'First qubit not in register'
        assert two < self.__size, 'Second qubit not in register'
        assert three < self.__size, 'Third qubit not in register'
        assert one != two and two != three and one != three, 'all qubits must be different'

        gate = gate.get_matrix()
        
        if self.__size > 3:
            tmp = cp.tile(cp.eye(2, dtype='complex'), (self.__size - 3, 1)).reshape(-1, 2, 2)
            tmp = utils.tensor_product_matrix_list(tmp)
            tmp = cp.kron(gate, tmp)
        else: 
            tmp = gate

        one = self.__appropriate_index(one)
        two = self.__appropriate_index(two)
        three = self.__appropriate_index(three)

        gate = utils.reorder_gate_three(tmp, one, two, three, self.__size)

        ops_matrix = self.__calculate_operators_product()

        self.__operators_matrix = gate @ ops_matrix

        self.__unapplied_gates = True
        self.__initialised = True

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
