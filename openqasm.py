from collections import defaultdict

#################### Macros ####################
identity = """gate id a { U(0,0,0) a; }\n"""

u3 = """gate u3(theta,phi,lambda) q { U(theta,phi,lambda) q; }\n"""

u2 = """gate u2(phi,lambda) q { U(pi/2,phi,lambda) q; }\n"""

rot = """gate u1(lambda) q { U(0,0,lambda) q; }\n"""

######################################

h = """gate h a { u2(0,pi) a; }"""

s = """gate s a { u1(pi/2) a; }"""

sdg = """gate sdg a { u1(-pi/2) a; }"""

t = """gate t a { u1(pi/4) a; }"""

tdg = """gate tdg a { u1(-pi/4) a; }"""

x = """gate x a { u3(pi,0,pi) a; }"""

y = """gate y a { u3(pi,pi/2,pi/2) a; }"""

z = """gate z a { u1(pi) a; }"""

rx = """gate rx(theta) a { u3(theta,-pi/2,pi/2) a; }"""

ry = """gate ry(theta) a { u3(theta,0,0) a; }"""

rz = """gate rz(phi) a { u1(phi) a; }"""

swap = """gate swap a, b {
    cx a,b;
    cx b,a;
    cx a,b;
}"""

######################################

cswap = """gate fredkin a, b, c {
    cx b,c;
    ccx a,c,b;
    cx b,c;
}"""

cx = """gate cx c,t { CX c,t; }"""

cy = """gate cy a,b { sdg b; cx a,b; s b; }"""

cz = """gate cz a,b { h b; cx a,b; h b; }""" 

crx = """gate crx(theta) a,b{
    cu3(theta, -pi/2, pi/2) a,b;
}"""

cry = """gate cry(theta) a,b{
    cu3(theta, 0, 0) a,b;
}"""

crz = """gate crz(lambda) a,b
{
u1(lambda/2) b;
cx a,b;
u1(-lambda/2) b;
cx a,b;
}"""

ct = """gate ct a,b{
    cu1(pi/4) a,b;
}"""

cs = """gate cs a,b{
    cu1(pi/2) a,b;
}"""

crot = """
gate cu1(lambda) a,b
{
u1(lambda/2) a;
cx a,b;
u1(-lambda/2) b;
cx a,b;
u1(lambda/2) b;
}"""

cu3 = """gate cu3(theta,phi,lambda) c, t
{
u1((lambda-phi)/2) t;
cx c,t;
u3(-theta/2,0,-(phi+lambda)/2) t;
cx c,t;
u3(theta/2,phi,0) t;
}"""

ccx = """gate ccx a,b,c
{
h c;
cx b,c; tdg c;
cx a,c; t c;
cx b,c; tdg c;
cx a,c; t b; t c; h c;
cx a,b; t a; tdg b;
cx a,b;
}"""
################################################

header = """OPENQASM 2.0;
include "qelib1.inc";"""

dependency_graph = {
    'swap': ['cx'],
    'cswap': ['cx', 'ccx'],
    'cy': ['s', 'sdg'],
    'cz': ['h'],
    'crx': ['cu3'],
    'ccx': ['h', 't', 'tdg']
}

dependency_graph = defaultdict(lambda: [], dependency_graph)

def list_to_qasm(list, circuit_size, filename: str):
    if filename.endswith('.qasm'):
        filename = filename[:-len('.qasm')]

    file = open(filename + '.qasm', 'w')

    file.write(header + '\n')

    prims = ['identity', 'rot', 'u2', 'u3', 'cx']
    added_deps = set()

    for prim in prims:
        file.write(globals()[prim] + '\n')
        added_deps.add(prim)

    ops = 'qreg q[{}];\n'.format(circuit_size)

    for gate, qubit_idx in list:
        add_dependencies(gate.name, added_deps, file)
        if gate.name not in added_deps:
            added_deps.add(gate.name)
            file.write(globals()[gate.name] + '\n')

        # Add it to ops (with params if present)
        params = '' if gate.params is None else '({})'.format(','.join(map(lambda x: str(x), gate.params)))
        if gate.name.startswith('c') or gate.name == 'swap':
            ops += '{}{} {};\n'.format(gate.name, params, ','.join(map(lambda x: 'qreq[' + str(x) + ']', qubit_idx)))
        else:
            for qubit in qubit_idx:
                ops += '{}{} q[{}];\n'.format(gate.name, params, qubit)

    file.write(ops)

    file.close()

def add_dependencies(gate_name, added_deps, file):
    for dep in dependency_graph[gate_name]:
        if dep not in added_deps:
            add_dependencies(dep, added_deps, file)
            file.write(globals()[dep] + '\n')