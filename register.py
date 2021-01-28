import cupy as cp

class QuantumRegister():
    # Have a set of common states
    zero = cp.array([1., 0.])
    one = cp.array([0.,1.])
    plus = cp.array([1/cp.sqrt(2), 1/cp.sqrt(2)])
    minus = cp.array([1/cp.sqrt(2), -1/cp.sqrt(2)])

    __one_test = cp.array(1.)

    def __init__(self, size):
        self.__size = size

        # Needed for efficiency purposes
        self.__dirty = True

        # Needed for correctness
        self.__initialised = False

        # initialise all states to zero
        self.__qubits = cp.stack([self.zero] * size, axis = 0)

    def get_register_size(self):
        return self.__size

    def initialise_qubit(self, index, state):
        assert not self.__initialised, 'Can not set states after adding a gate'

        assert index < self.__size, 'Qubit not in register'
        
        cp.testing.assert_array_equal(cp.around(cp.sum(cp.absolute(state) ** 2)), self.__one_test, 'Non-quantum mechanical state', False)

        self.__dirty = True 
        self.__qubits[index] = state

    def get_statevector(self):
        if self.__dirty:
            # TODO: if time allows, make this more efficient
            if self.__size > 1:
                self.__statevector = cp.kron(self.__qubits[0], self.__qubits[1])

                for i in range(2, self.__size):
                    self.__statevector = cp.kron(self.__statevector, self.__qubits[i])
            else:
                self.__statevector = self.__qubits[0]

        self.__dirty = True

        return self.__statevector


    def add_gate(self):
        self.__initialised = True
        pass

    def measure(self, shots):
        statevector = self.get_statevector()
        values, counts = cp.unique(cp.random.choice(len(statevector), shots, p=cp.absolute(statevector) ** 2), return_counts=True)
        values = list(cp.asnumpy(values))
        values = [format(i, '0' + str(self.__size) + 'b') for i in values]
        res = dict([i for i in zip(values, list(cp.asnumpy(counts)))])
        return res
