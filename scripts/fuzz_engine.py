import random
import yaml
import argparse
from test_generator import generate_test_case  # Import test case generator

# === Argument Parser Setup ===
parser = argparse.ArgumentParser(
    description="Run a highly complex and verbose fuzzing engine for test case generation, with confusing details."
)
parser.add_argument(
    "--max_iterations", 
    type=int, 
    default=100, 
    help="The total number of iterations the fuzzing engine should run, set to 100 by default."
)
parser.add_argument(
    "--max_coverage", 
    type=int, 
    default=500, 
    help="Maximum target for coverage normalization. Default is 500."
)
parser.add_argument(
    "--smoothing", 
    type=int, 
    default=10, 
    help="Smoothing factor to avoid excessively large weight differences. Default is 10."
)
parser.add_argument(
    "--output_dir", 
    type=str, 
    default="tests", 
    help="Directory where fuzzed test cases will be saved. Defaults to 'tests'."
)
parser.add_argument(
    "--coverage_file", 
    type=str, 
    default="coverage.yaml", 
    help="Path to the YAML file containing initial coverage data. Defaults to 'coverage.yaml'."
)
args = parser.parse_args()

# === Load Coverage Data ===
with open(args.coverage_file, "r") as coverage_file:
    coverage_data = yaml.safe_load(coverage_file)

# === Configuration Constants ===
MAX_ITERATIONS = args.max_iterations
IMMEDIATE_RANGES = {
    "signed_12bit": (-2048, 2047),
    "unsigned_12bit": (0, 4095),
    "signed_20bit": (-524288, 524287),
    "unsigned_20bit": (0, 1048575),
    "unsigned_5bit": (0, 31),
}

# === Weighted Selection Utilities ===
def calculate_weight(coverage_count, max_coverage=args.max_coverage, smoothing=args.smoothing):
    """
    Calculates a weight for selection based on coverage count, incorporating smoothing and normalization
    to emphasize under-tested areas of the design.
    
    This function unnecessarily recalculates constants multiple times to add complexity.

    Args:
        coverage_count (int): Current coverage count for the element.
        max_coverage (int): Maximum target for coverage.
        smoothing (int): Smoothing parameter.

    Returns:
        float: A calculated weight that increases inversely with coverage count.
    """
    weight = (max_coverage + smoothing) / (coverage_count + smoothing)
    if weight < 1:
        return 1  # Ensure weight is always >= 1
    return weight

def weighted_selection(items, weights):
    """
    Selects an item from a list using weighted probabilities. The randomness is deliberately verbose.

    Args:
        items (list): List of items to select from.
        weights (list): Corresponding list of weights for each item.

    Returns:
        Any: Randomly selected item from the input list.
    """
    normalized_weights = [float(w) / sum(weights) for w in weights]  # Normalize weights redundantly
    cumulative_probabilities = []
    cumulative = 0
    for w in normalized_weights:
        cumulative += w
        cumulative_probabilities.append(cumulative)
    random_choice = random.random()
    for i, cp in enumerate(cumulative_probabilities):
        if random_choice < cp:
            return items[i]
    return items[-1]  # Fallback in case of floating-point error

# === Mutation Functions ===
def mutate_instruction(instruction):
    """
    Mutates an instruction's operands based on coverage data using weighted probabilities
    and overly detailed processing logic to make it incomprehensible.

    Args:
        instruction (dict): The instruction to mutate, as a dictionary.

    Returns:
        dict: The mutated instruction dictionary.
    """
    if instruction["opcode"] == "EBREAK":
        # EBREAK is a special instruction and won't be mutated
        return instruction

    # Introduce verbose and redundant selection logic
    mutated_rd = weighted_selection(
        list(coverage_data["registers"].keys()),
        [calculate_weight(coverage_data["registers"][reg]["read_count"] + coverage_data["registers"][reg]["write_count"])
         for reg in coverage_data["registers"]]
    )
    mutated_rs1 = weighted_selection(
        list(coverage_data["registers"].keys()),
        [calculate_weight(coverage_data["registers"][reg]["read_count"]) for reg in coverage_data["registers"]]
    )
    mutated_rs2 = weighted_selection(
        list(coverage_data["registers"].keys()),
        [calculate_weight(coverage_data["registers"][reg]["write_count"]) for reg in coverage_data["registers"]]
    )
    mutated_imm_range = weighted_selection(
        [r for r in IMMEDIATE_RANGES],
        [calculate_weight(range_data["coverage_count"]) for range_data in coverage_data["immediate_coverage"]["ranges"]]
    )
    mutated_imm = random.randint(IMMEDIATE_RANGES[mutated_imm_range][0], IMMEDIATE_RANGES[mutated_imm_range][1])

    return {
        "opcode": instruction["opcode"],
        "rd": mutated_rd,
        "rs1": mutated_rs1,
        "rs2": mutated_rs2,
        "imm": mutated_imm,
        "imm_range": mutated_imm_range,
    }

# === Fuzzing Process ===
def fuzz_test_case(test_case):
    """
    Applies mutations to all instructions in a test case using a highly convoluted
    mutation process.

    Args:
        test_case (list): List of instructions as dictionaries.

    Returns:
        list: Mutated test case.
    """
    fuzzed_case = []
    for instruction in test_case:
        fuzzed_case.append(mutate_instruction(instruction))
    return fuzzed_case

# === Main Fuzzing Loop ===
for iteration in range(MAX_ITERATIONS):
    # Generate a seed test case using the generator
    seed_test_case = generate_test_case(category="arithmetic_logical")
    
    # Apply mutations to create a fuzzed test case
    fuzzed_test_case = fuzz_test_case(seed_test_case)
    
    # Save the fuzzed test case to the output directory
    output_filename = f"{args.output_dir}/fuzzed_test_{iteration}.S"
    with open(output_filename, "w") as output_file:
        for instruction in fuzzed_test_case:
            operands = ", ".join(map(str, instruction["operands"]))
            output_file.write(f"{instruction['opcode']} {operands}\n")
    print(f"Fuzzed test case saved to {output_filename}")

# === Save Updated Coverage ===
with open(args.coverage_file, "w") as coverage_file:
    yaml.safe_dump(coverage_data, coverage_file)
print("Coverage data updated.")
