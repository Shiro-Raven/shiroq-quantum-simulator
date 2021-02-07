try:
    import cupy as np
except ModuleNotFoundError:
    try:
        import numpy as np
    except ModuleNotFoundError:
        print('Neither CuPy nor NumPy are installed')
    
from gate import QuantumGate
import utils
from openqasm import list_to_qasm

import math
from datetime import datetime
import warnings

class QuantumRegister():
    # Have a set of common states
    zero = np.array([1., 0.], dtype='complex')
    one = np.array([0.,1.], dtype='complex')
    plus = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype='complex')
    minus = np.array([1/np.sqrt(2), -1/np.sqrt(2)], dtype='complex')

    __one_test = np.array(1.)

    def __init__(self, size, endianness='big'):
        assert size < 26, 'Maximum allowed qubits is 25'
        assert size > 0, 'Can not have empty register'

        self.set_endianness(endianness)
        self.__size = size

        self.reset()

    def reset(self):
        # operations list
        self.__operations = list()

        # Needed for efficiency purposes
        self.__dirty = True
        self.__unapplied_gates = False
        self.__opmatrix_calculated = False

        # Needed for correctness
        self.__initialised = False

        # initialise all states to zero
        self.__qubits = np.stack([self.zero] * self.__size, axis = 0)

        self.__gate_cache = np.tile(np.eye(2, dtype='complex'), (self.__size, 1)).reshape(-1, 2, 2)
        self.__operators_matrix = np.eye(2 ** self.__size)


    def get_register_size(self):
        return self.__size

    def set_endianness(self, endianness):
        assert endianness in ['big', 'little'], 'Endianness can only be big or little'
        self.__is_big_endian = endianness == 'big'

    def get_endianness(self):
        return 'big' if self.__is_big_endian else 'little'

    def run_program(self, program, global_params=None, reversed=False):
        assert isinstance(program, list), 'Program must be a list'

        # Reverse the operations of the program (eg. can be to run QFT_dag from QFT program)
        if reversed:
            program.reverse()

        # Go through each instruction (read, gate) and retrieve its parameters
        for instruction in program:
            params = instruction[:-1]

            # Replace the global parameters
            for i in range(1, len(params)):
                if isinstance(params[i], str):
                    assert params[i] in global_params.keys(), 'Global parameter not provided!'

                    params[i] = global_params[params[i]]
            
            # Create the gate with the captured parameters
            gate = QuantumGate(*params)

            # Add the gate to the circuit
            self.add_gate(gate, instruction[-1])

        self.apply()

    def __appropriate_index(self, index):
        return index if self.__is_big_endian else self.__size - index - 1

    def initialise_qubit(self, index, state):
        assert not self.__initialised, 'Can not set states after adding a gate'
        assert index < self.__size, 'Qubit not in register'
        np.testing.assert_array_equal(np.around(np.sum(np.absolute(state) ** 2)), self.__one_test, 'Non-quantum mechanical state', False)

        index = self.__appropriate_index(index)

        self.__dirty = True 
        self.__qubits[index] = state

    def get_statevector(self):
        if self.__dirty:
            # TODO: if time allows, make this more efficient
            self.__statevector = utils.tensor_product_vector_list(self.__qubits)

        self.__dirty = False

        return self.__statevector


    def store_as_qasm(self, filename=datetime.now().strftime("%d/%m/%Y-%H:%M:%S"), qubits_to_measure=None):
        assert all([target < self.__size for target in qubits_to_measure]) \
            if qubits_to_measure is not None else True, 'Some qubits not in register'

        if qubits_to_measure is not None: 
            qubits_to_measure = [self.__appropriate_index(qubit) for qubit in qubits_to_measure]

        list_to_qasm(self.__operations, self.__size, filename, qubits_to_measure)
        return

    def add_gate(self, gate, targets):
        self.__do_assertions(gate, targets)

        self.__operations.append((gate, targets))

        # First, retrieve the matrix from the Gate object and correct the indexing
        gate = gate.get_matrix()

        for i in range(len(targets)):
            targets[i] =  self.__appropriate_index(targets[i])

        affected_qubits = int(math.log(gate.shape[0], 2))
        ############################################
        if affected_qubits == 1:
            # If a single qubit gate, simply add it to the qubits caches
            for target in targets:
                target = self.__appropriate_index(target)
                self.__gate_cache[target] = gate @ self.__gate_cache[target]
            self.__opmatrix_calculated = False
        else:
            # If a multi-qubit gate is needed, accumulate the caches to be able to apply it 
            if self.__size > affected_qubits:
                tmp = np.tile(np.eye(2, dtype='complex'), (self.__size - affected_qubits, 1)).reshape(-1, 2, 2)
                tmp = utils.tensor_product_matrix_list(tmp)
                tmp = np.kron(gate, tmp)
            else:
                tmp = gate

            gate = utils.reorder_gate(tmp, self.__size, self.__is_big_endian, *targets)

            ops_matrix = self.__calculate_operators_product()

            self.__operators_matrix = gate @ ops_matrix
        ############################################

        self.__unapplied_gates = True
        self.__initialised = True

    def __do_assertions(self, gate, targets):
        """
        Just a bunch of assertions to check the sanity of the gate parameters
        """
        assert all([target < self.__size for target in targets]), 'Some qubits not in register'
        assert len(targets) == len(set(targets)), 'All target qubits must be different!'
        
        affected_qubits = int(math.log(gate.get_matrix().shape[0], 2))
        assert affected_qubits <= self.__size, 'Gate too big for circuit'
        
        if affected_qubits > 1:
            assert affected_qubits == len(targets), 'Too many/too few arguments for target qubits'

    def __calculate_operators_product(self):
        """
        Accumulates all the cached gates and returns their unitary
        """
        if not self.__opmatrix_calculated:
            tmp = utils.tensor_product_matrix_list(self.__gate_cache)
            self.__operators_matrix = tmp @ self.__operators_matrix 
            self.__gate_cache = np.tile(np.eye(2, dtype='complex'), (self.__size, 1)).reshape(-1, 2, 2)

        self.__opmatrix_calculated = True

        return self.__operators_matrix

    def apply(self):
        if not self.__unapplied_gates:
            return
        self.__unapplied_gates = False

        # Simply retrieve the statevector and the unitary and multiply
        statevector = self.get_statevector()
        operators_matrix = self.__calculate_operators_product()

        self.__statevector = operators_matrix @ statevector

        self.__operators_matrix = np.eye(2 ** self.__size)

    def measure(self, shots, qubits_idx=None):
        assert qubits_idx is None or isinstance(qubits_idx, list), 'Incorrect way of indexing qubits'
        
        if qubits_idx == None:
            qubits_idx = [self.__appropriate_index(i) for i in range(self.__size)]
        else:
            qubits_idx = [self.__appropriate_index(i) for i in qubits_idx]

        assert max(qubits_idx) < self.__size or min(qubits_idx) >= 0, 'Some qubits not in register'

        if self.__unapplied_gates:
            warnings.warn('Some gates are not applied yet! Call QuantumRegister.apply()')

        # Retrieve the statevector and sample from it
        statevector = self.get_statevector()
        values, counts = np.unique(np.random.choice(len(statevector), shots, p=np.absolute(statevector) ** 2), return_counts=True)
        
        # Convert to binary
        try:
            values = list(np.asnumpy(values))
        except: 
            values = list(values)
        values = [format(i, '0' + str(self.__size) + 'b') for i in values]

        # Cherrypick the needed qubits
        res = dict()
        for i, value in enumerate(values):
            key = ''.join([value[i] for i in qubits_idx])
            if key in res.keys():
                res[key] += counts[i].item()
            else:
                res[key] = counts[i].item()

        return res