import yaml
import random

# Load instruction templates
with open("insn_template.yaml", "r") as file:
    insn_templates = yaml.safe_load(file)

# Register list and other operand constraints
registers = [f"x{i}" for i in range(32)]
immediate_ranges = {
    "signed_12bit": (-2048, 2047),
    "unsigned_12bit": (0, 4095),
    "signed_20bit": (-524288, 524287),
    "unsigned_20bit": (0, 1048575),
    "unsigned_5bit": (0, 31)
}

# Random generator functions for values
def random_register():
    return random.choice(registers)

def random_immediate(constraint):
    min_val, max_val = immediate_ranges.get(constraint, (0, 1))
    return random.randint(min_val, max_val)

# Generate a single instruction based on category and constraints
def generate_instruction(category):
    # Randomly select an instruction within the given category
    instructions = [
        insn for insn in insn_templates['instructions']['RV32I']
        if insn_templates['instructions']['RV32I'][insn].get('category') == category
    ]
    insn_data = random.choice([insn_templates['instructions']['RV32I'][insn] for insn in instructions])

    # Create the assembly line for the instruction
    mnemonic = insn_data['mnemonic']
    operands = []

    for operand in insn_data['operands']:
        operand_type = list(operand.values())[0]

        # Initialize operand_value based on type
        operand_value = None
        if operand_type == "reg":
            operand_value = f"x{random.randint(0, 31)}"
        elif operand_type == "signed_12bit":
            min_val, max_val = map(int, insn_data['constraints']['imm_range'].split(" to "))
            operand_value = random.randint(min_val, max_val)
        elif operand_type == "unsigned_12bit":
            min_val, max_val = map(int, insn_data['constraints']['imm_range'].split(" to "))
            operand_value = random.randint(min_val, max_val)
        elif operand_type == "signed_20bit":
            min_val, max_val = map(int, insn_data['constraints']['offset_range'].split(" to "))
            operand_value = random.randint(min_val, max_val)
        elif operand_type == "unsigned_20bit":
            min_val, max_val = map(int, insn_data['constraints']['imm_range'].split(" to "))
            operand_value = random.randint(min_val, max_val)
        elif operand_type == "unsigned_5bit":
            min_val, max_val = map(int, insn_data['constraints']['shamt_range'].split(" to "))
            operand_value = random.randint(min_val, max_val)

        operands.append(operand_value)

    # Return formatted instruction
    return f"{mnemonic} " + ", ".join(str(op) for op in operands)



# Generate the test code with 50 instructions
def generate_test_code(category):
    nops = ["addi x0, x0, 0x0"] * 3
    code = nops.copy()

    for _ in range(50):
        instruction = generate_instruction(category)
        code.append(instruction)

    code.extend(nops)
    return code

# Write to a .S file
def write_test_file(category, filename="test_programs/test_program.S"):
    test_code = generate_test_code(category)
    with open(filename, "w") as file:
        for line in test_code:
            file.write(line + "\n")
    print(f"Test program written to {filename}")

# Usage
if __name__ == "__main__":
    write_test_file("arithmetic_logical")
    #print(insn_templates['instructions']['RV32I']['ADDI']['category'])
    #testdump = [test for test,data in insn_templates['instructions']['RV32I'].items() if data.get('category')=='arithmetic_logical']
    #print(testdump)

