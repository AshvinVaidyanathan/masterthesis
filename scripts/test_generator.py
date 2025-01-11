import yaml
import random

# === Load Instruction Templates ===
with open("insn_template.yaml", "r") as file:
    insn_templates = yaml.safe_load(file)

# === Configuration ===
registers = [f"x{i}" for i in range(32)]  # List of RISC-V registers
immediate_ranges = {
    "signed_12bit": (-2048, 2047),
    "unsigned_12bit": (0, 4095),
    "signed_20bit": (-524288, 524287),
    "unsigned_20bit": (0, 1048575),
    "unsigned_5bit": (0, 31),
}

# === Utility Functions ===
def random_register():
    """Select a random register."""
    return random.choice(registers)

def random_immediate(range_key):
    """Generate a random immediate value within the specified range."""
    min_val, max_val = immediate_ranges.get(range_key, (0, 1))
    return random.randint(min_val, max_val)

# === Instruction Generation ===
def generate_instruction(category=None, mnemonic=None):
    """
    Generate a single instruction based on a specific category or mnemonic.
    Args:
        category (str): Instruction category, e.g., 'arithmetic_logical'.
        mnemonic (str): Specific instruction mnemonic, e.g., 'ADDI'.
    Returns:
        dict: Generated instruction as a dictionary.
    """
    if mnemonic:
        instructions = [
            insn for insn in insn_templates["instructions"]["RV32I"]
            if insn_templates["instructions"]["RV32I"][insn].get("mnemonic") == mnemonic
        ]
    elif category:
        instructions = [
            insn for insn in insn_templates["instructions"]["RV32I"]
            if insn_templates["instructions"]["RV32I"][insn].get("category") == category
        ]
    else:
        raise ValueError("Either 'category' or 'mnemonic' must be specified.")

    if not instructions:
        raise ValueError(f"No instructions found for category={category} or mnemonic={mnemonic}.")

    insn_data = random.choice([insn_templates["instructions"]["RV32I"][insn] for insn in instructions])

    mnemonic = insn_data["mnemonic"]
    operands = []

    for operand in insn_data["operands"]:
        operand_type = list(operand.values())[0]
        if operand_type == "reg":
            value = random_register()
        elif operand_type in immediate_ranges:
            value = random_immediate(operand_type)
        else:
            raise ValueError(f"Unsupported operand type: {operand_type}")
        operands.append(value)

    return {"opcode": mnemonic, "operands": operands}

# === Test Case Generation ===
def generate_test_case(category=None, mnemonic=None):
    """
    Generate a test case consisting of 50 instructions based on category or mnemonic.
    Args:
        category (str): Instruction category, e.g., 'arithmetic_logical'.
        mnemonic (str): Specific instruction mnemonic, e.g., 'ADDI'.
    Returns:
        list: List of generated instructions as dictionaries.
    """
    nops = [{"opcode": "ADDI", "operands": ["x0", "x0", 0]}] * 3
    instructions = nops.copy()

    for _ in range(50):
        instruction = generate_instruction(category=category, mnemonic=mnemonic)
        instructions.append(instruction)

    instructions.extend(nops)
    return instructions

# === Instruction Validation ===
def validate_instruction(instruction, template):
    """
    Validate that the instruction matches the expected format and constraints.
    Args:
        instruction (dict): The generated instruction.
        template (dict): Corresponding template for validation.
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        opcode, operands = instruction["opcode"], instruction["operands"]

        # Validate opcode
        if opcode != template["mnemonic"]:
            raise ValueError(f"Opcode mismatch: {opcode} != {template['mnemonic']}")

        # Validate operands
        for i, operand in enumerate(operands):
            expected_type = list(template["operands"][i].values())[0]
            if expected_type == "reg" and operand not in registers:
                raise ValueError(f"Invalid register: {operand}")
            elif expected_type in immediate_ranges:
                min_val, max_val = immediate_ranges[expected_type]
                if not (min_val <= operand <= max_val):
                    raise ValueError(f"Immediate {operand} out of range for {expected_type}")
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False

# === File Writing ===
def write_test_file(test_case, filename="test_programs/test_program.S"):
    """Write the test case to a file in assembly format."""
    with open(filename, "w") as file:
        for instruction in test_case:
            operands = ", ".join(map(str, instruction["operands"]))
            file.write(f"{instruction['opcode']} {operands}\n")
    print(f"Test program written to {filename}")

# === Example Usage ===
if __name__ == "__main__":
    test_case = generate_test_case(category="arithmetic_logical")
    write_test_file(test_case)
