from gate import QuantumGate


def parse_program(program):
    if isinstance(program, str):
        # Open the file containing the program
        program = open(program, "r")

        # Evaluate to a list of dicts
        program = program.readlines()
        program = "".join(program).replace("\n", "")
        program = eval(program)

    assert isinstance(program, list), "Only can read a list of dicts"

    return _parse_list(program)


def _parse_list(program_list):
    # Transform dicts to parameters
    params = list()
    for instruction in program_list:
        instr_params = list()

        instr_params.append(instruction["gate"])

        if instruction["gate"][0] == "c":
            tmp = instruction["gate"][1:]
        else:
            tmp = instruction["gate"]

        if tmp.lower() in QuantumGate.single_parameter_gates:
            instr_params.append(instruction["params"]["theta"])
        elif tmp.lower() == "u3":
            instr_params.append(instruction["params"]["theta"])
            instr_params.append(instruction["params"]["phi"])
            instr_params.append(instruction["params"]["lambda"])

        instr_params.append(instruction["target"])
        params.append(instr_params)

    return params
