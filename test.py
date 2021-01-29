from register import QuantumRegister
import utils
from gate import QuantumGate
import cupy as cp

"""
reg = QuantumRegister(3)

reg.initialise_qubit(0, QuantumRegister.one)
reg.initialise_qubit(1, QuantumRegister.plus)

x_gate = QuantumGate('X')
z_gate = QuantumGate('Z')
h_gate = QuantumGate('H')
y_gate = QuantumGate('Y')

reg.add_single_qubit_gate(x_gate, [0])
reg.add_single_qubit_gate(z_gate, [1])
reg.add_single_qubit_gate(h_gate, [1])
reg.add_single_qubit_gate(y_gate, [2])
#cp.absolute(cp.kron(cp.kron(reg.foo(0), reg.foo(1)), reg.foo(2)) @ reg.get_statevector())
reg.apply_batch()
"""
reg = QuantumRegister(2)

#reg.initialise_qubit(7, QuantumRegister.one)

h = QuantumGate('H')

reg.add_single_qubit_gate(h, [0])
reg.apply()
tmp = reg.measure(10)
reg.set_endianness('little')
reg.add_single_qubit_gate(h, [0])
reg.apply()
breakpoint()