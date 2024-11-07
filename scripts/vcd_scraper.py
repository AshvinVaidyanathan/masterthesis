from vcd.reader import TokenKind, tokenize
import re

# Define alias-to-name mapping
alias_to_name = {
    "c!": "count_cycle",
    "~\"": "cpu_state",
    "L": "dbg_insn_opcode",
    "x\"": "dbg_insn_rd",
    "s": "dbg_insn_rs1",
    "w\"": "dbg_insn_rs2",
    "y#": "dbg_reg_x0",
    "N": "dbg_reg_x1",
    "O": "dbg_reg_x2",
    "P": "dbg_reg_x3",
    "Q": "dbg_reg_x4",
    "R": "dbg_reg_x5",
    "S": "dbg_reg_x6",
    "T": "dbg_reg_x7",
    "U": "dbg_reg_x8",
    "V": "dbg_reg_x9",
    "W": "dbg_reg_x10",
    "X": "dbg_reg_x11",
    "Y": "dbg_reg_x12",
    "Z": "dbg_reg_x13",
    "[": "dbg_reg_x14",
    "\\":"dbg_reg_x15",
    "]": "dbg_reg_x16",
    "^": "dbg_reg_x17",
    "_": "dbg_reg_x18",
    "`": "dbg_reg_x19",
    "a": "dbg_reg_x20",
    "b": "dbg_reg_x21",
    "c": "dbg_reg_x22",
    "d": "dbg_reg_x23",
    "e": "dbg_reg_x24",
    "f": "dbg_reg_x25",
    "g": "dbg_reg_x26",
    "h": "dbg_reg_x27",
    "i": "dbg_reg_x28",
    "j": "dbg_reg_x29",
    "k": "dbg_reg_x30",
    "l": "dbg_reg_x31",
    "b#": "mem_axi_rdata",
    "R!": "mem_axi_addr",
    "T!": "mem_axi_wdata"

}


# Initialize signal values and tracking variables
signal_values = {alias: None for alias in alias_to_name}
log_output = []
previous_count_cycle = None
inside_test_code = False
log_final_nops = False  # Track final NOPs for logging
nop_count = 0  # Track consecutive NOPs

def is_nop():
    """Function to check if current signals indicate a NOP instruction"""
    return (signal_values.get("L") == 1)  # Update with actual NOP opcode

# Open the VCD file in binary mode
with open('/home/ashvin/thesis/scratch/testpico/testbench.vcd', 'rb') as vcd_file:
    for token in tokenize(vcd_file):
        if token.kind == TokenKind.TIMESCALE:
            clock_cycle = token.data

        elif token.kind == TokenKind.CHANGE_SCALAR or token.kind == TokenKind.CHANGE_VECTOR:
            signal_alias = token.data[0]
            if signal_alias in alias_to_name:
                # Update the signal's current value
                signal_values[signal_alias] = token.data[1]
                
                # Check for the NOP sequence to start/stop logging
                if is_nop():
                    nop_count += 1
                else:
                    nop_count = 0
                
                # Print the NOP status for debugging
                #print(f"NOP count: {nop_count}, Inside test code: {inside_test_code}")

                # Start logging if the first three NOPs are detected
                if nop_count == 3 and not inside_test_code:
                    inside_test_code = True
                    log_output.append("Starting test code section...")
                    print("Entering test code section")
                
                # End logging if another set of three NOPs is detected
                elif nop_count == 3 and inside_test_code:
                    inside_test_code = False
                    log_final_nops = True  # Start logging the last three NOPs
                    log_output.append("Ending test code section...")
                    print("Exiting test code section")
                
                # Log final three NOPs after exiting test code
                if log_final_nops:
                    if nop_count > 0:
                        log_entry = (
                            f"{clock_cycle} " + ",".join(
                                f"{alias_to_name[alias]}={signal_values[alias]}" if alias in ['c!', 'x\"', 's', 'w\"'] and signal_values[alias] is not None
                                else f"{alias_to_name[alias]}={hex(signal_values[alias])}" if signal_values[alias] is not None
                                else f"{alias_to_name[alias]}=None"
                                for alias in alias_to_name
                            )
                        )
                        log_output.append(log_entry)
                        #print(log_entry)  # Debugging print

                    # Reset after logging final three NOPs
                    if nop_count == 3:
                        log_final_nops = False

                # If inside test code, log the necessary signals
                elif inside_test_code and signal_alias == "c!":
                    current_count_cycle = token.data[1]
                    if current_count_cycle != previous_count_cycle:
                        log_entry = (
                            f"{clock_cycle} " + ",".join(
                                f"{alias_to_name[alias]}={signal_values[alias]}" if alias in ['c!', 'x\"', 's', 'w\"'] and signal_values[alias] is not None
                                else f"{alias_to_name[alias]}={hex(signal_values[alias])}" if signal_values[alias] is not None
                                else f"{alias_to_name[alias]}=None"
                                for alias in alias_to_name
                            )
                        )
                        log_output.append(log_entry)
                        #print(log_entry)  # Debugging print
                        previous_count_cycle = current_count_cycle



def extract_and_format_spike_log(spike_log_file, output_file):
    """
    Extracts and formats the section in the spike log between the first and last sequence of three consecutive NOP instructions,
    excluding trailing NOPs, and writes the formatted output to a file.

    Args:
        spike_log_file (str): Path to the spike log file.
        output_file (str): Path to the output file where formatted log will be saved.
    """
    nop_sequence = "(0x0001)"  # NOP instruction pattern
    within_section = False
    nop_streak = 0
    formatted_lines = []

    with open(spike_log_file, 'r') as file:
        for line in file:
            if nop_sequence in line:
                nop_streak += 1
            else:
                nop_streak = 0

            if nop_streak == 3 and not within_section:
                within_section = True
                continue

            if within_section and nop_streak < 3:
                # Match instruction line and optional register
                match = re.match(
                    r"core\s+\d+:\s+\d+\s+(0x[0-9a-f]+)\s+\((0x[0-9a-f]+)\)(?:\s+(x\d+)\s+(0x[0-9a-f]+))?",
                    line
                )
                # Match memory operation if present
                mem_match = re.search(r"mem\s+(0x[0-9a-f]+)\s+(0x[0-9a-f]+)", line)

                if match:
                    pc = match.group(1)
                    instruction = match.group(2)
                    reg = match.group(3) if match.group(3) else "n/a"
                    reg_value = match.group(4) if match.group(4) else "n/a"
                    mem = mem_match.group(1) if mem_match else "n/a"
                    mem_value = mem_match.group(2) if mem_match else "n/a"
                    
                    formatted_line = f"pc={pc}, instruction={instruction}, reg={reg}, reg_value={reg_value}, mem={mem}, mem_value={mem_value}"
                    formatted_lines.append(formatted_line)

            if within_section and nop_streak == 3:
                break

    # Write all lines except the last two to the output file
    with open(output_file, 'w') as out_file:
        for line in formatted_lines[:-2]:
            out_file.write(line + "\n")
            print(line)  # Optional: print to console

# Usage
spike_log_file = "/home/ashvin/thesis/scratch/spiketest/spike_log.txt"
output_file = "/home/ashvin/thesis/scratch/testpico/logscripts/log_spike.txt"
#extract_and_format_spike_log(spike_log_file, output_file)

print("Spike log file created: logscripts/log_spike.txt")


# Write the collected log entries to a file
with open('/home/ashvin/thesis/scratch/testpico/logscripts/log_vcd.txt', 'w') as log_file:
    for entry in log_output:
        log_file.write(entry + "\n")

print("Log file created: logscripts/log_vcd.txt")
