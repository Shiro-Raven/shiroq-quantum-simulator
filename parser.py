
def parse_program(file_path):
    # Open the file containing the program
    program_file = open(file_path, "r")

    # Evaluate to a list of dicts
    program_list = program_file.readlines()
    program_list = ''.join(program_list).replace('\n', '')
    program_list = eval(program_list)

    # Transform dicts to parameters
    params = list()
    for instruction in program_list:
        instr_params = list()
        
        instr_params.append(instruction['gate'])

        if instruction['gate'].lower() in ['rx', 'ry', 'rz']:
            instr_params.append(instruction['params']['theta'])
        elif instruction['gate'].lower() == 'u3':
            instr_params.append(instruction['params']['theta'])
            instr_params.append(instruction['params']['phi'])
            instr_params.append(instruction['params']['lambda'])

        instr_params.append(instruction['target'])
        params.append(instr_params)

    return params