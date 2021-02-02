# ShiroQ Quantum Computer Simulator :cyclone:
This is a simple quantum computer simulator implemented in Python as the screening task for [QOSF](https://qosf.org/)'s Quantum Computing Mentorship Program.

## Pre-requisites
- [NumPy](https://numpy.org/)
- [CuPy](https://cupy.dev/) (Optional, needed for GPU acceleration)
- [Matplotlib](https://matplotlib.org/)

## Features
- Support for most common single-qubit quantum gates, as well as the Toffoli and Swap gates, along with their controlled versions.
- Support for the parametric R<sub>x</sub>, R<sub>y</sub>, R<sub>z</sub>, and U<sub>3</sub>.
- Ability to run variational quantum algorithms.
Examples can be found in the __notebooks__ folder.

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
    
- Automated Circuit Building
    1. Instead of manually adding gates, one can parse a list of dictionaries containing the configurations of the different gates of the circuit. First, inintialise the circuit similar to steps 1 and 2 above. Then, the list has to be passed to ```parse_program``` function in ```utils.py```. The path to a file containing the list can also be used.
    ```python
    circuit_conf = [
  { "gate": "h", "target": [0] }, 
  { "gate": "cx", "target": [0, 1] }
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