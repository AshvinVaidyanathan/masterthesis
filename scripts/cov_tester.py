import re
import yaml
from collections import defaultdict

# Load the coverage.yaml structure
with open("/home/ashvin/thesis/scratch/fuzz/coverage.yaml", "r") as file:
    coverage_data = yaml.safe_load(file)

# Patterns to extract relevant fields from each line
pattern = re.compile(
    r"dbg_insn_opcode=(0x[0-9a-fA-F]+),dbg_insn_rd=(\d+),dbg_insn_rs1=(\d+),dbg_insn_rs2=(\d+)"
)
register_pattern = re.compile(r"dbg_reg_x(\d+)=(0x[0-9a-fA-F]+)")

# Initialize tracking for coverage
executed_instructions = defaultdict(int)
register_access = defaultdict(lambda: {"read": 0, "write": 0})
immediate_ranges = {
    "signed_8bit_range": (-128, 127),
    "signed_12bit_range": (-2048, 2047),
    "unsigned_16bit_range": (0, 65535)
}

# Helper function to check immediate coverage
def check_immediate_coverage(value):
    for range_name, (min_val, max_val) in immediate_ranges.items():
        if min_val <= value <= max_val:
            coverage_data["functional_coverage"]["immediate_coverage"]["ranges"].append({
                "range": range_name, "covered": True
            })

# Process the log file
with open("log_vcd.txt", "r") as log_file:
    for line in log_file:
        # Parse instruction fields
        match = pattern.search(line)
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

# Save the updated coverage data
with open("updated_coverage.yaml", "w") as file:
    yaml.dump(coverage_data, file)

print("Coverage data updated and saved to updated_coverage.yaml")
