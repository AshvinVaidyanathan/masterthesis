import random
import math
import yaml
fimport argparse
from test_generator import generate_test_case  # Import the test case generator function

# Set up argument parsing for command-line options
parser = argparse.ArgumentParser(description="Run a coverage-guided fuzzing engine for test case generation.")

parser.add_argument("--max_iterations", type=int, default=100, help="Number of fuzzing iterations to run (default: 100).")
parser.add_argument("--max_coverage", type=int, default=500, help="Max coverage target to normalize weights (default: 500).")
parser.add_argument("--smoothing", type=int, default=10, help="Smoothing factor for weight calculation (default: 10).")
parser.add_argument("--output_dir", type=str, default="tests", help="Directory to save generated test cases (default: 'tests').")
parser.add_argument("--coverage_file", type=str, default="coverage.yaml", help="Path to coverage data file (default: 'coverage.yaml').")

args = parser.parse_args()

# Load initial configuration and coverage data
with open("coverage.yaml", "r") as coverage_file:
    coverage_data = yaml.safe_load(coverage_file)

# Define fuzz engine parameters
MAX_ITERATIONS = 100  # Total number of fuzzing iterations to perform
IMMEDIATE_RANGES = {
    "signed_12bit": (-2048, 2047),
    "unsigned_12bit": (0, 4095),
    "signed_20bit": (-524288, 524287),
    "unsigned_20bit": (0, 1048575),
    "unsigned_5bit": (0, 31),
}

# Function to calculate weight based on coverage using a smoothing parameter
# Higher weights are assigned to lower coverage counts
def calculate_weight(coverage_count, max_coverage=500, smoothing=10):
    """
    Calculate a weight for selection based on the coverage count.
    Uses a smooth inverse proportional weighting system to emphasize
    under-covered areas.

    Args:
        coverage_count (int): The current coverage count for a specific range or register.
        max_coverage (int): The maximum target for coverage; default is 500.
        smoothing (int): Smoothing factor to avoid excessive weight at zero coverage.

    Returns:
        float: A calculated weight value, where higher values correspond to lower coverage.
    """
    return max(1, (max_coverage + smoothing) / (coverage_count + smoothing))

# Function to select an immediate range with weighted probability based on coverage
def weighted_immediate_range():
    """
    Selects an immediate range for fuzzing based on coverage data.
    Less-covered ranges receive higher probabilities for selection.

    Returns:
        str: The key of the selected immediate range.
    """
    ranges = coverage_data["immediate_coverage"]["ranges"]
    range_choices = []
    weights = []

    # Iterate through ranges and calculate weights based on current coverage count
    for range_info in ranges:
        range_key = list(range_info.keys())[0]
        coverage_count = range_info[range_key]["coverage_count"]
        weight = calculate_weight(coverage_count)
        range_choices.append(range_key)
        weights.append(weight)

    # Randomly select a range, biased by calculated weights
    return random.choices(range_choices, weights=weights, k=1)[0]

# Generate a random immediate value within a given range key
def fuzz_immediate(range_key):
    """
    Generates a random immediate value within the specified range.

    Args:
        range_key (str): Key indicating the immediate range (e.g., 'signed_12bit').

    Returns:
        int: Randomly generated immediate value within the specified range.
    """
    min_val, max_val = IMMEDIATE_RANGES[range_key]
    return random.randint(min_val, max_val)

# Function to select a register with weighted probability based on coverage
def weighted_register():
    """
    Selects a register for fuzzing based on coverage data.
    Registers with lower coverage receive higher weights for selection.

    Returns:
        str: The name of the selected register (e.g., 'x5').
    """
    register_choices = []
    weights = []

    # Calculate weights for each register based on read and write counts
    for reg, reg_data in coverage_data["registers"].items():
        coverage_count = reg_data["read_count"] + reg_data["write_count"]
        weight = calculate_weight(coverage_count)
        register_choices.append(reg)
        weights.append(weight)

    # Select a register with probability weighted by coverage
    return random.choices(register_choices, weights=weights, k=1)[0]

# Function to apply mutations with weighted selection, with exception for EBREAK
def mutate_instruction(instruction):
    """
    Mutates an instruction's operands based on weighted selection.
    If the instruction is an 'EBREAK', it is returned unmodified.

    Args:
        instruction (dict): The instruction dictionary containing fields like 'opcode', 'rd', etc.

    Returns:
        dict: The mutated or original instruction.
    """
    # Skip mutation if the instruction is EBREAK
    if instruction["opcode"] == "EBREAK":
        return instruction

    # Apply weighted fuzzing for other instructions
    instruction["imm"] = fuzz_immediate(instruction["imm_range"])
    instruction["rd"] = weighted_register()
    instruction["rs1"] = weighted_register()
    instruction["rs2"] = weighted_register()
    return instruction

# Placeholder for updating coverage after each test case run
def update_coverage(test_case_path, coverage_data):
    """
    Updates the coverage data based on the results of a test case.
    This function would parse execution logs and update 'coverage.yaml'.

    Args:
        test_case_path (str): Path to the executed test case file.
        coverage_data (dict): The in-memory coverage data dictionary to be updated.
    """
    # Insert logic to parse simulation results and update coverage data here
    pass

# Main fuzzing loop with weighted selection
for i in range(MAX_ITERATIONS):
    # 1. Select an immediate range with weighted probability for fuzzing
    selected_range = weighted_immediate_range()
    immediate_value = fuzz_immediate(selected_range)

    # 2. Generate a new test case with weighted register and immediate values
    instructions = []
    for j in range(50):  # Generate 50 instructions per test case
        # Add EBREAK as the last instruction in each test case for consistency
        if j == 49:
            base_instruction = {"opcode": "EBREAK"}
        else:
            # Define the base instruction structure
            base_instruction = {
                "opcode": random.choice(["ADD", "SUB", "MUL", "DIV"]),
                "rd": weighted_register(),
                "rs1": weighted_register(),
                "rs2": weighted_register(),
                "imm": immediate_value,
                "imm_range": selected_range
            }

        # Apply mutation to the instruction and add it to the test case
        mutated_instruction = mutate_instruction(base_instruction)
        instructions.append(mutated_instruction)

    # 3. Generate test case source code from the mutated instructions
    test_case = generate_test_case(instructions)

    # 4. Save the generated test case to a file
    test_case_path = f"tests/fuzzed_test_{i}.s"
    with open(test_case_path, "w") as test_file:
        test_file.write(test_case)

    # 5. Execute test case and update coverage data
    # Execute the test case and collect results (simulate this step)
    # Insert actual test execution logic as needed
    # After execution, parse results and update coverage
    update_coverage(test_case_path, coverage_data)

# 6. Save the updated coverage data
with open("coverage.yaml", "w") as coverage_file:
    yaml.safe_dump(coverage_data, coverage_file)
