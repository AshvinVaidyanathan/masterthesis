#include "Vpicorv32_wrapper.h"
#include "verilated_vcd_c.h"

int main(int argc, char **argv, char **env)
{
	printf("Built with %s %s.\n", Verilated::productName(), Verilated::productVersion());
	printf("Recommended: Verilator 4.0 or later.\n");

	Verilated::commandArgs(argc, argv);
	Vpicorv32_wrapper* top = new Vpicorv32_wrapper;

	// Tracing (vcd)
	VerilatedVcdC* tfp = NULL;
	const char* flag_vcd = Verilated::commandArgsPlusMatch("vcd");
	if (flag_vcd && 0==strcmp(flag_vcd, "+vcd")) {
		Verilated::traceEverOn(true);
		tfp = new VerilatedVcdC;
		top->trace (tfp, 99);
		tfp->open("testbench.vcd");
	}

	// Tracing (data bus, see showtrace.py)
	FILE *trace_fd = NULL;
	const char* flag_trace = Verilated::commandArgsPlusMatch("trace");
	if (flag_trace && 0==strcmp(flag_trace, "+trace")) {
		trace_fd = fopen("testbench.trace", "w");
	}

	top->clk = 0;
	int t = 0;
	while (!Verilated::gotFinish()) {
		if (t > 200)
			top->resetn = 1;
		top->clk = !top->clk;
		top->eval();
		if (tfp) tfp->dump (t);
		// if (trace_fd && top->clk && top->trace_valid) fprintf(trace_fd, "Cycle %d: trace_data = %9.9lx, opcode = %x, rd = %x, rs1 = %x, rs2 = %x, imm = %x, addr = %x\n",
		// 	        t, top->trace_data,
		// 	        top->dbg_insn_opcode, // Capture instruction opcode
		// 	        top->dbg_insn_rd,     // Capture destination register
		// 	        top->dbg_insn_rs1,    // Capture source register 1
		// 	        top->dbg_insn_rs2,    // Capture source register 2
		// 	        top->dbg_insn_imm,    // Capture immediate value
		// 	        top->dbg_insn_addr    // Capture instruction address
		// 	);
		t += 5;
	}
	if (tfp) tfp->close();
	delete top;
	exit(0);
}

