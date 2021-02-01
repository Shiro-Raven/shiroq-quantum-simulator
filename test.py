from register import QuantumRegister
import utils
from gate import QuantumGate
import cupy as cp
import parser


reg = QuantumRegister(3)

reg.set_endianness('little')

#reg.initialise_qubit(0, QuantumRegister.one)
#reg.initialise_qubit(1, QuantumRegister.one)

breakpoint()

prog = parser.parse_program('./sample_circuits/Simple_grover.txt')

#prog = parser.parse_program('./sample_circuits/Fredkin_gate.txt')

reg.run_program(prog)

breakpoint()