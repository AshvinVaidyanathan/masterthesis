import re
import yaml
from collections import defaultdict

# Load the coverage.yaml structure
with open("/home/ashvin/thesis/scratch/fuzz/coverage.yaml", "r") as file:
    coverage_data = yaml.safe_load(file)

# Patterns to extract relevant fields from each line
instruction_pattern = re.compile(
    r"dbg_insn_opcode=(0x[0-9a-fA-F]+),dbg_insn_rd=(\d+),dbg_insn_rs1=(\d+),dbg_insn_rs2=(\d+)"
)
register_pattern = re.compile(r"dbg_reg_x(\d+)=(0x[0-9a-fA-F]+)")
pc_pattern = re.compile(r"dbg_pc=(0x[0-9a-fA-F]+)")

# Initialize tracking for coverage and bugs
executed_instructions = defaultdict(int)
register_access = defaultdict(lambda: {"read": 0, "write": 0})
immediate_hit_counts = defaultdict(int)  # Track hits for each range
bug_logs = []

# Load immediate ranges dynamically from coverage.yaml
immediate_ranges = {}
for range_item in coverage_data["functional_coverage"]["immediate_coverage"]["ranges"]:
    range_name = range_item["range"]
    range_bounds = range_item["bounds"]
    immediate_ranges[range_name] = (range_bounds["min"], range_bounds["max"])

# Helper function to check immediate coverage
def check_immediate_coverage(value):
    """
    Check if an immediate value falls within any defined range
    and increment hit counts for covered ranges.
    """
    for range_name, (min_val, max_val) in immediate_ranges.items():
        if min_val <= value <= max_val:
            immediate_hit_counts[range_name] += 1
            coverage_data["functional_coverage"]["immediate_coverage"]["ranges"][range_name]["covered"] = True

# Bug categorization function (unchanged)
def classify_bug(observed, expected):
    if observed["pc"] != expected["pc"]:
        return "Control Flow Bug"
    elif observed["registers"] != expected["registers"]:
        return "Functional Bug"
    elif observed.get("memory") != expected.get("memory"):
        return "Memory Access Bug"
    else:
        return "Unknown Bug"

# Process the log file
with open("log_vcd.txt", "r") as log_file:
    for line in log_file:
        # Parse program counter
        pc_match = pc_pattern.search(line)
        current_pc = pc_match.group(1) if pc_match else None

        # Parse instruction fields
        match = instruction_pattern.search(line)
        if match:
            opcode, rd, rs1, rs2 = match.groups()
            executed_instructions[opcode] += 1
            register_access[rd]["write"] += 1
            register_access[rs1]["read"] += 1
            register_access[rs2]["read"] += 1

        # Parse register values and check immediate coverage
        for reg_match in register_pattern.finditer(line):
            reg_num, reg_value = reg_match.groups()
            reg_int_value = int(reg_value, 16)
            check_immediate_coverage(reg_int_value)

        # Compare observed vs. expected state (unchanged)
        expected_state = {
            "pc": current_pc,  # Expected PC from coverage model (add logic to fetch this)
            "registers": {},  # Expected register values (add logic to fetch this)
        }
        observed_state = {
            "pc": current_pc,
            "registers": {f"x{reg_num}": reg_value for reg_num, reg_value in register_pattern.findall(line)},
        }

        if observed_state != expected_state:
            bug_type = classify_bug(observed_state, expected_state)
            bug_logs.append({
                "type": bug_type,
                "pc": current_pc,
                "instruction": opcode,
                "observed": observed_state,
                "expected": expected_state
            })

# Update coverage data
for instruction, count in executed_instructions.items():
    if instruction in coverage_data["functional_coverage"]["instruction_set_coverage"]["instructions"]:
        coverage_data["functional_coverage"]["instruction_set_coverage"]["instructions"][instruction]["executed"] = True
        coverage_data["functional_coverage"]["instruction_set_coverage"]["instructions"][instruction]["execution_count"] = count

for reg_num, access_data in register_access.items():
    reg_name = f"x{reg_num}"
    if reg_name in coverage_data["functional_coverage"]["register_coverage"]["registers"]:
        coverage_data["functional_coverage"]["register_coverage"]["registers"][reg_name]["accessed"] = True
        coverage_data["functional_coverage"]["register_coverage"]["registers"][reg_name]["write_count"] = access_data["write"]
        coverage_data["functional_coverage"]["register_coverage"]["registers"][reg_name]["read_count"] = access_data["read"]

# Add immediate range hit counts to coverage.yaml
for range_name, hit_count in immediate_hit_counts.items():
    coverage_data["functional_coverage"]["immediate_coverage"]["ranges"][range_name]["hit_count"] = hit_count

# Save the updated coverage data
with open("updated_coverage.yaml", "w") as file:
    yaml.dump(coverage_data, file)

# Save the bug logs
with open("bug_logs.yaml", "w") as file:
    yaml.dump(bug_logs, file)

print("Coverage data updated and saved to updated_coverage.yaml")
print("Bug logs saved to bug_logs.yaml")
