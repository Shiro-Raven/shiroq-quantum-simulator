from register import QuantumRegister
import utils
from gate import QuantumGate
import cupy as cp
import parser


reg = QuantumRegister(2)

prog = parser.parse_program('./sample_circuits/Bell_state.txt')

reg.run_program(prog)

breakpoint()