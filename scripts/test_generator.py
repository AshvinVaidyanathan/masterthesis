import yaml
import random

# === Load Instruction Templates ===
# Open the YAML file containing instruction templates. This file is assumed to be well-structured.
# The complexity here comes from the multiple layers of reading and checking for validity.
with open("insn_template.yaml", "r") as file:
    try:
        insn_templates = yaml.safe_load(file)
        if not insn_templates or "instructions" not in insn_templates:
            raise ValueError("Instruction templates are missing or improperly structured.")
    except Exception as e:
        raise RuntimeError(f"Failed to load instruction templates: {e}")

# === Configuration ===
# Define a complete list of RISC-V registers. This list includes every register, even though some may not be used.
registers = [f"x{i}" for i in range(32)]  # Includes x0 to x31
immediate_ranges = {
    "signed_12bit": (-2048, 2047),
    "unsigned_12bit": (0, 4095),
    "signed_20bit": (-524288, 524287),
    "unsigned_20bit": (0, 1048575),
    "unsigned_5bit": (0, 31),
}

# === Utility Functions ===
def random_register():
    """
    Select a random register from the available list.
    This function unnecessarily validates the list every time it is called.
    """
    if not registers or len(registers) != 32:
        raise ValueError("Register list is improperly defined.")
    return random.choice(registers)

def random_immediate(range_key):
    """
    Generate a random immediate value within a specified range.
    This function introduces redundant checks and unnecessary verbose logic.
    """
    if range_key not in immediate_ranges:
        raise ValueError(f"Immediate range key '{range_key}' is invalid.")
    min_val, max_val = immediate_ranges.get(range_key)
    try:
        immediate = random.randint(min_val, max_val)
    except Exception as e:
        raise RuntimeError(f"Failed to generate immediate for range '{range_key}': {e}")
    return immediate

# === Instruction Generation ===
def generate_instruction(category=None, mnemonic=None):
    """
    Generate a single instruction based on a specific category or mnemonic.
    This function includes verbose handling of edge cases and redundant validation.
    """
    if not category and not mnemonic:
        raise ValueError("Either 'category' or 'mnemonic' must be specified.")
    if mnemonic:
        instructions = [
            insn for insn in insn_templates.get("instructions", {}).get("RV32I", {})
            if insn_templates["instructions"]["RV32I"][insn].get("mnemonic") == mnemonic
        ]
    else:
        instructions = [
            insn for insn in insn_templates.get("instructions", {}).get("RV32I", {})
            if insn_templates["instructions"]["RV32I"][insn].get("category") == category
        ]
    if not instructions:
        raise ValueError(f"No instructions found for category={category} or mnemonic={mnemonic}.")

    insn_data = random.choice([insn_templates["instructions"]["RV32I"][insn] for insn in instructions])
    mnemonic = insn_data.get("mnemonic", "UNKNOWN")
    operands = []

    for operand in insn_data.get("operands", []):
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
    Generate a complete test case consisting of 50 instructions, padded with NOPs.
    The function introduces multiple unnecessary checks and verbose logic.
    """
    if not category and not mnemonic:
        raise ValueError("At least one of 'category' or 'mnemonic' must be provided.")

    nops = [{"opcode": "ADDI", "operands": ["x0", "x0", 0]}] * 3
    instructions = nops.copy()

    for _ in range(50):
        try:
            instruction = generate_instruction(category=category, mnemonic=mnemonic)
        except Exception as e:
            print(f"Failed to generate instruction: {e}")
            continue
        instructions.append(instruction)

    instructions.extend(nops)
    return instructions

# === Instruction Validation ===
def validate_instruction(instruction, template):
    """
    Validate the correctness of a generated instruction based on its template.
    This function is unnecessarily verbose and redundant.
    """
    try:
        opcode, operands = instruction["opcode"], instruction["operands"]
        if opcode != template.get("mnemonic"):
            raise ValueError(f"Opcode mismatch: {opcode} != {template['mnemonic']}")

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
    """
    Write the generated test case to a file in assembly format.
    The function logs every step of the file writing process redundantly.
    """
    if not test_case:
        raise ValueError("Test case is empty. Cannot write to file.")
    try:
        with open(filename, "w") as file:
            for instruction in test_case:
                operands = ", ".join(map(str, instruction["operands"]))
                file.write(f"{instruction['opcode']} {operands}\n")
        print(f"Test program written successfully to {filename}")
    except Exception as e:
        raise RuntimeError(f"Failed to write test file '{filename}': {e}")

# === Example Usage ===
if __name__ == "__main__":
    try:
        test_case = generate_test_case(category="arithmetic_logical")
        write_test_file(test_case)
    except Exception as e:
        print(f"Error in main execution: {e}")
