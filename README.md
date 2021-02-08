# :boom: ShiroQ Quantum Computer Simulator :cyclone:
This is a simple quantum computer simulator implemented in Python as the screening task for [QOSF](https://qosf.org/)'s Quantum Computing Mentorship Program.

## Pre-requisites
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [CuPy](https://cupy.dev/) (Optional, needed for GPU acceleration)
- [SciPy](https://www.scipy.org/scipylib/index.html) (Suggested for variational quantum algorithms, using its ```optimize```)

## Features
- Support for most common single-qubit quantum gates, as well as the Toffoli and Swap gates, along with their controlled versions.
- Support for the parametric R<sub>x</sub>, R<sub>y</sub>, R<sub>z</sub>,  U<sub>1</sub>, and U<sub>3</sub> gates.
- Ability to run variational quantum algorithms.
- OpenQASM translator to run your circuits on other frameworks and real hardware (or even apply some [ZX-calculus magic](https://github.com/Quantomatic/pyzx)).

Examples can be found in the __notebooks__ folder.

## Components

The simulator consists of the following components:

- ``register.py``: This is where most of the magic happens. This file contains the ``QuantumRegister`` class which contains most of the simulators logic.
- ``gate.py``: This file is responsible for creating reusable instances of all supported gates that can be added to your quantum register, using the ``QuantumGate`` class. 
- ``program_parser.py``: This file contains the logic for parsing a program as detailed in the explanation of the task, and compiling the parameters needed for runnning that program in our ``QuantumRegister``.
- ``utils.py``: This file contains some helper functions for calculating tensor products, reordering the wiring of a quantum gate, and creating an arbitrary state from Bloch sphere angles with a global phase, and plotting counts.
- ``openqasm.py``: This file contains the translation to OpenQASM logic.

## Usage
- Manual Circuit Building
    1. The circuit logic is contained in the ``QuantumRegister`` class. To start, initialise a register with a set size, with all qubits initialised to the ground state:
    ```python
    example_reg = QuantumRegister(5)
    ```
    2. One can then initialise any of the qubits to any sound quantum state. The common base states {0, 1, +, -} are available from the class for convenience. Note that big endian indexing is used by default. If one prefers little endian indexing, the function ``set_endianness`` can be used:
    ```python
    example_reg.initialise_qubit(0, QuantumRegister.plus)
    ```
    3. Once you are happy with the initial qubit states, you can start adding gates to your circuit, by passing the gate and the target qubits. For this, the ```QuantumGate``` class can be used as a gate builder. Just pass the gate name to the constructor: 
    ```python
    x_gate = QuantumGate('X')
    controlled_z = QuantumGate('cz')
    controlled_u3 = QuantumGate('cu3', 3.1415, 0, -1.5707)
    example_reg.add_gate(x_gate, [0,1,2])
    example_reg.add_gate(controlled_z, [0, 4])
    example_reg.add_gate(controlled_u3, [0])
    ```
    4. Adding gates to the circuit does not automatically apply them to the current state of the system. For this, you need to call the ```apply``` function simply as follows:
    ```python
    example_reg.apply()
    ```
    5. To carry out a measurement, pass the number of shots and the qubits you want to measure as parameters to the measurement function. The function returns a dictionary of the measured states:
    ```python
    results_dict = example_reg.measure(1000) # Implicit measurement of all qubits
    first_qubit_dict = example_reg.measure(1000, [0]) # Explicit choice of qubits
    ```
    6. If you wish to transform the added gates to a QASM file, simply call the translator's function. Note that measurement operators need to be explicitly passed to the translator as indices of the qubits to be measured.
    ```python
    example_reg.store_as_qasm('sample_filename', [0 ,1, 2])
    ```
    
- Automated Circuit Building
    1. Instead of manually adding gates, one can parse a list of dictionaries containing the configurations of the different gates of the circuit. First, inintialise the circuit similar to steps 1 and 2 above. Then, the list has to be passed to ```parse_program``` function in ```utils.py```. The path to a file containing the list can also be used.
    ```python
    circuit_conf = [
  { "gate": "h", "target": [0] }, 
  { "gate": "cx", "target": [0, 1] },
  { "gate": "u1", "params" : {"theta": 3.14159265}, "target": [0, 1] },
    ]
    
    parsed_program = parser.parse_program(circuit_conf)
    ```
    2. Afterwards, the ```run_program``` of ```QuantumRegister``` must be invoked of the parsed list. This function automatically applies any outstanding gates to the state of the system, unlike before.
    ```python
    example_reg.run_program(parsed_program)
    ```
    3. Several programs can be run consequently. One can also use both approaches to build circuits (remember to call ```apply``` if final addition of gates was manual!):
    ```python
    example_reg.run_program(program_1)
    
    example_reg.add_gate(QuantumGate('H'), [0,2,1])
    
    example_reg.run_program(program_2)
    ```
