from register import QuantumRegister
import utils
from gate import QuantumGate
import cupy as cp
import parser


reg = QuantumRegister(3)

reg.set_endianness('little')

reg.initialise_qubit(0, QuantumRegister.one)
reg.initialise_qubit(1, QuantumRegister.one)
reg.initialise_qubit(2, QuantumRegister.zero)

breakpoint()

prog = parser.parse_program('./sample_circuits/Fredkin_gate.txt')

#prog = parser.parse_program('./sample_circuits/Simple_grover.txt')

#reg.run_program(prog)

#reg.add_single_qubit_gate(QuantumGate('x'), [0,1])

#prog = parser.parse_program('./sample_circuits/Bell_state.txt')

reg.run_program(prog)

breakpoint()