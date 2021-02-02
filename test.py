from register import QuantumRegister
import utils
from gate import QuantumGate
import cupy as cp
import parser


reg = QuantumRegister(1)

reg.set_endianness('little')

#reg.initialise_qubit(0, QuantumRegister.one)
#reg.initialise_qubit(1, QuantumRegister.one)

breakpoint()

prog = parser.parse_program('./sample_circuits/Variational_algorithm.txt')

#prog = parser.parse_program('./sample_circuits/Fredkin_gate.txt')

reg.run_program(prog, { "global_1": 3.1415, "global_2": 1.5708 })

breakpoint()