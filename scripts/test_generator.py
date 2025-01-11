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

# === Weighted Selection Functions ===
def calculate_weight(coverage_count, max_coverage=500, smoothing=10):
    """Calculate a weight for selection based on coverage count."""
    return max(1, (max_coverage + smoothing) / (coverage_count + smoothing))

def weighted_register(coverage_data):
    """Select a register with weighted probability based on coverage."""
    register_choices = []
    weights = []
    for reg, reg_data in coverage_data["registers"].items():
        coverage_count = reg_data["read_count"] + reg_data["write_count"]
        weight = calculate_weight(coverage_count)
        register_choices.append(reg)
        weights.append(weight)
    return random.choices(register_choices, weights=weights, k=1)[0]

def weighted_immediate_range(coverage_data):
    """Select an immediate range with weighted probability based on coverage."""
    range_choices = []
    weights = []
    for range_info in coverage_data["immediate_coverage"]["ranges"]:
        for range_key, range_data in range_info.items():
            coverage_count = range_data["coverage_count"]
            weight = calculate_weight(coverage_count)
            range_choices.append(range_key)
            weights.append(weight)
    return random.choices(range_choices, weights=weights, k=1)[0]

# === Instruction Generation ===
def generate_instruction(category=None, mnemonic=None, mutate=False, coverage_data=None):
    """
    Generate a single instruction based on a specific category or mnemonic.
    Args:
        category (str): Instruction category, e.g., 'arithmetic_logical'.
        mnemonic (str): Specific instruction mnemonic, e.g., 'ADDI'.
        mutate (bool): Whether to apply mutations based on coverage data.
        coverage_data (dict): Coverage data for guided fuzzing.
    Returns:
        str: Generated instruction.
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
            value = weighted_register(coverage_data) if mutate and coverage_data else random_register()
        elif operand_type in immediate_ranges:
            range_key = weighted_immediate_range(coverage_data) if mutate and coverage_data else operand_type
            value = random_immediate(range_key)
        else:
            raise ValueError(f"Unsupported operand type: {operand_type}")
        operands.append(value)

    return f"{mnemonic} " + ", ".join(map(str, operands))

# === Instruction Validation ===
def validate_instruction(instruction, template):
    """
    Validate that the instruction matches the expected format and constraints.
    Args:
        instruction (str): The generated instruction.
        template (dict): Corresponding template for validation.
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        mnemonic, *operands = instruction.split()

        # Validate mnemonic
        if mnemonic != template["mnemonic"]:
            raise ValueError(f"Mnemonic mismatch: {mnemonic} != {template['mnemonic']}")

        # Validate operands
        for i, operand in enumerate(operands):
            expected_type = list(template["operands"][i].values())[0]
            if expected_type == "reg" and operand not in registers:
                raise ValueError(f"Invalid register: {operand}")
            elif expected_type in immediate_ranges:
                value = int(operand)
                min_val, max_val = immediate_ranges[expected_type]
                if not (min_val <= value <= max_val):
                    raise ValueError(f"Immediate {value} out of range for {expected_type}")
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False

# === Test Case Generation ===
def generate_test_code(category=None, mnemonic=None, mutate=False, coverage_data=None):
    """
    Generate test code consisting of 50 instructions based on category or mnemonic.
    Args:
        category (str): Instruction category, e.g., 'arithmetic_logical'.
        mnemonic (str): Specific instruction mnemonic, e.g., 'ADDI'.
        mutate (bool): Whether to apply mutations.
        coverage_data (dict): Coverage data for fuzzing.
    Returns:
        list: List of validated instructions.
    """
    nops = ["addi x0, x0, 0x0"] * 3
    code = nops.copy()

    for _ in range(50):
        instruction = generate_instruction(category=category, mnemonic=mnemonic, mutate=mutate, coverage_data=coverage_data)
        template = random.choice([
            insn_templates["instructions"]["RV32I"][insn]
            for insn in insn_templates["instructions"]["RV32I"]
            if insn_templates["instructions"]["RV32I"][insn]["mnemonic"] == instruction.split()[0]
        ])
        if validate_instruction(instruction, template):
            code.append(instruction)
        else:
            print(f"Invalid instruction skipped: {instruction}")

    code.extend(nops)
    return code

# === File Writing ===
def write_test_file(category=None, mnemonic=None, filename="test_programs/test_program.S", mutate=False, coverage_data=None):
    """
    Write the test code to a file.
    """
    test_code = generate_test_code(category=category, mnemonic=mnemonic, mutate=mutate, coverage_data=coverage_data)
    with open(filename, "w") as file:
        for line in test_code:
            file.write(line + "\n")
    print(f"Test program written to {filename}")

# === Example Usage ===
if __name__ == "__main__":
    mock_coverage_data = {
        "registers": {f"x{i}": {"read_count": random.randint(0, 50), "write_count": random.randint(0, 50)} for i in range(32)},
        "immediate_coverage": {"ranges": [{"signed_12bit": {"coverage_count": random.randint(0, 50)}}]}
    }

    write_test_file(category="arithmetic_logical", mutate=True, coverage_data=mock_coverage_data)
    write_test_file(mnemonic="ADDI", filename="test_programs/test_program_addi.S", mutate=True, coverage_data=mock_coverage_data)
