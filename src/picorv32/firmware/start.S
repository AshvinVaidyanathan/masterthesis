// This is free and unencumbered software released into the public domain.
//
// Anyone is free to copy, modify, publish, use, compile, sell, or
// distribute this software, either in source code form or as a compiled
// binary, for any purpose, commercial or non-commercial, and by any
// means.

#define ENABLE_QREGS
#define ENABLE_HELLO
#undef ENABLE_RVTST
#undef ENABLE_SIEVE
#undef ENABLE_MULTST
#undef ENABLE_STATS

#ifndef ENABLE_QREGS
#  undef ENABLE_RVTST
#endif

// Only save registers in IRQ wrapper that are to be saved by the caller in
// the RISC-V ABI, with the excpetion of the stack pointer. The IRQ handler
// will save the rest if necessary. I.e. skip x3, x4, x8, x9, and x18-x27.
#undef ENABLE_FASTIRQ

#include "custom_ops.S"

	.section .text
	.global irq
	.global hello
	.global sieve
	.global multest
	.global hard_mul
	.global hard_mulh
	.global hard_mulhsu
	.global hard_mulhu
	.global hard_div
	.global hard_divu
	.global hard_rem
	.global hard_remu
	.global stats

reset_vec:
	// no more than 16 bytes here !
	picorv32_waitirq_insn(zero)
	picorv32_maskirq_insn(zero, zero)
	j start


/* Interrupt handler
 **********************************/

.balign 16
irq_vec:
	/* save registers */

#ifdef ENABLE_QREGS

	picorv32_setq_insn(q2, x1)
	picorv32_setq_insn(q3, x2)

	lui x1, %hi(irq_regs)
	addi x1, x1, %lo(irq_regs)

	picorv32_getq_insn(x2, q0)
	sw x2,   0*4(x1)

	picorv32_getq_insn(x2, q2)
	sw x2,   1*4(x1)

	picorv32_getq_insn(x2, q3)
	sw x2,   2*4(x1)

#ifdef ENABLE_FASTIRQ
	sw x5,   5*4(x1)
	sw x6,   6*4(x1)
	sw x7,   7*4(x1)
	sw x10, 10*4(x1)
	sw x11, 11*4(x1)
	sw x12, 12*4(x1)
	sw x13, 13*4(x1)
	sw x14, 14*4(x1)
	sw x15, 15*4(x1)
	sw x16, 16*4(x1)
	sw x17, 17*4(x1)
	sw x28, 28*4(x1)
	sw x29, 29*4(x1)
	sw x30, 30*4(x1)
	sw x31, 31*4(x1)
#else
	sw x3,   3*4(x1)
	sw x4,   4*4(x1)
	sw x5,   5*4(x1)
	sw x6,   6*4(x1)
	sw x7,   7*4(x1)
	sw x8,   8*4(x1)
	sw x9,   9*4(x1)
	sw x10, 10*4(x1)
	sw x11, 11*4(x1)
	sw x12, 12*4(x1)
	sw x13, 13*4(x1)
	sw x14, 14*4(x1)
	sw x15, 15*4(x1)
	sw x16, 16*4(x1)
	sw x17, 17*4(x1)
	sw x18, 18*4(x1)
	sw x19, 19*4(x1)
	sw x20, 20*4(x1)
	sw x21, 21*4(x1)
	sw x22, 22*4(x1)
	sw x23, 23*4(x1)
	sw x24, 24*4(x1)
	sw x25, 25*4(x1)
	sw x26, 26*4(x1)
	sw x27, 27*4(x1)
	sw x28, 28*4(x1)
	sw x29, 29*4(x1)
	sw x30, 30*4(x1)
	sw x31, 31*4(x1)
#endif

#else // ENABLE_QREGS

#ifdef ENABLE_FASTIRQ
	sw gp,   0*4+0x200(zero)
	sw x1,   1*4+0x200(zero)
	sw x2,   2*4+0x200(zero)
	sw x5,   5*4+0x200(zero)
	sw x6,   6*4+0x200(zero)
	sw x7,   7*4+0x200(zero)
	sw x10, 10*4+0x200(zero)
	sw x11, 11*4+0x200(zero)
	sw x12, 12*4+0x200(zero)
	sw x13, 13*4+0x200(zero)
	sw x14, 14*4+0x200(zero)
	sw x15, 15*4+0x200(zero)
	sw x16, 16*4+0x200(zero)
	sw x17, 17*4+0x200(zero)
	sw x28, 28*4+0x200(zero)
	sw x29, 29*4+0x200(zero)
	sw x30, 30*4+0x200(zero)
	sw x31, 31*4+0x200(zero)
#else
	sw gp,   0*4+0x200(zero)
	sw x1,   1*4+0x200(zero)
	sw x2,   2*4+0x200(zero)
	sw x3,   3*4+0x200(zero)
	sw x4,   4*4+0x200(zero)
	sw x5,   5*4+0x200(zero)
	sw x6,   6*4+0x200(zero)addi x0, x0, 0x0
addi x0, x0, 0x0
addi x0, x0, 0x0
SUB x2, x7, x12
SRAI x4, x26, 3
ORI x12, x25, -887
SLTI x15, x5, 751
SLTI x5, x6, -79
SLL x24, x27, x9
SUB x21, x29, x8
XOR x18, x16, x4
ORI x20, x15, 981
OR x25, x23, x9
XOR x11, x23, x10
XOR x31, x30, x30
ADDI x6, x23, -391
SLLI x29, x13, 4
SLL x9, x30, x0
SRAI x8, x31, 29
OR x11, x15, x23
SLT x18, x13, x20
SRAI x0, x18, 28
SRAI x0, x27, 12
SRLI x8, x25, 7
SRL x15, x30, x1
OR x7, x1, x23
ADD x24, x31, x25
AND x14, x24, x30
ADDI x15, x18, 218
XOR x2, x10, x18
SRA x27, x9, x3
XOR x20, x2, x6
SLTIU x5, x29, 2468
XOR x18, x22, x31
SRA x22, x20, x13
SLTU x22, x12, x14
SLTU x18, x1, x30
SRAI x13, x30, 0
AND x22, x4, x18
SRAI x18, x16, 9
AND x16, x5, x22
ANDI x28, x31, -1853
SLTI x14, x13, -158
AND x18, x12, x26
SLTIU x6, x3, 1484
SRL x15, x11, x5
SLLI x8, x29, 10
XOR x7, x30, x20
SLTI x3, x22, 1973
SLT x20, x13, x29
SLTI x12, x18, 1785
SRA x15, x19, x18
ORI x1, x10, -489
addi x0, x0, 0x0
addi x0, x0, 0x0
addi x0, x0, 0x0
)
	sw x11, 11*4+0x200(zero)
	sw x12, 12*4+0x200(zero)
	sw x13, 13*4+0x200(zero)
	sw x14, 14*4+0x200(zero)
	sw x15, 15*4+0x200(zero)
	sw x16, 16*4+0x200(zero)
	sw x17, 17*4+0x200(zero)
	sw x18, 18*4+0x200(zero)
	sw x19, 19*4+0x200(zero)
	sw x20, 20*4+0x200(zero)
	sw x21, 21*4+0x200(zero)
	sw x22, 22*4+0x200(zero)
	sw x23, 23*4+0x200(zero)
	sw x24, 24*4+0x200(zero)
	sw x25, 25*4+0x200(zero)
	sw x26, 26*4+0x200(zero)
	sw x27, 27*4+0x200(zero)
	sw x28, 28*4+0x200(zero)
	sw x29, 29*4+0x200(zero)
	sw x30, 30*4+0x200(zero)
	sw x31, 31*4+0x200(zero)
#endif

#endif // ENABLE_QREGS

	/* call interrupt handler C function */

	lui sp, %hi(irq_stack)
	addi sp, sp, %lo(irq_stack)

	// arg0 = address of regs
	lui a0, %hi(irq_regs)
	addi a0, a0, %lo(irq_regs)

	// arg1 = interrupt type
#ifdef ENABLE_QREGS
	picorv32_getq_insn(a1, q1)
#else
	addi a1, tp, 0
#endif

	// call to C function
	jal ra, irq

	/* restore registers */

#ifdef ENABLE_QREGS

	// new irq_regs address returned from C code in a0
	addi x1, a0, 0

	lw x2,   0*4(x1)
	picorv32_setq_insn(q0, x2)

	lw x2,   1*4(x1)
	picorv32_setq_insn(q1, x2)

	lw x2,   2*4(x1)
	picorv32_setq_insn(q2, x2)

#ifdef ENABLE_FASTIRQ
	lw x5,   5*4(x1)
	lw x6,   6*4(x1)
	lw x7,   7*4(x1)
	lw x10, 10*4(x1)
	lw x11, 11*4(x1)
	lw x12, 12*4(x1)
	lw x13, 13*4(x1)
	lw x14, 14*4(x1)
	lw x15, 15*4(x1)
	lw x16, 16*4(x1)
	lw x17, 17*4(x1)
	lw x28, 28*4(x1)
	lw x29, 29*4(x1)
	lw x30, 30*4(x1)
	lw x31, 31*4(x1)
#else
	lw x3,   3*4(x1)
	lw x4,   4*4(x1)
	lw x5,   5*4(x1)
	lw x6,   6*4(x1)
	lw x7,   7*4(x1)
	lw x8,   8*4(x1)
	lw x9,   9*4(x1)
	lw x10, 10*4(x1)
	lw x11, 11*4(x1)
	lw x12, 12*4(x1)
	lw x13, 13*4(x1)
	lw x14, 14*4(x1)
	lw x15, 15*4(x1)
	lw x16, 16*4(x1)
	lw x17, 17*4(x1)
	lw x18, 18*4(x1)
	lw x19, 19*4(x1)
	lw x20, 20*4(x1)
	lw x21, 21*4(x1)
	lw x22, 22*4(x1)
	lw x23, 23*4(x1)
	lw x24, 24*4(x1)
	lw x25, 25*4(x1)
	lw x26, 26*4(x1)
	lw x27, 27*4(x1)
	lw x28, 28*4(x1)
	lw x29, 29*4(x1)
	lw x30, 30*4(x1)
	lw x31, 31*4(x1)
#endif

	picorv32_getq_insn(x1, q1)
	picorv32_getq_insn(x2, q2)

#else // ENABLE_QREGS

	// new irq_regs address returned from C code in a0
	addi a1, zero, 0x200
	beq a0, a1, 1f
	ebreak
1:

#ifdef ENABLE_FASTIRQ
	lw gp,   0*4+0x200(zero)
	lw x1,   1*4+0x200(zero)
	lw x2,   2*4+0x200(zero)
	lw x5,   5*4+0x200(zero)
	lw x6,   6*4+0x200(zero)
	lw x7,   7*4+0x200(zero)
	lw x10, 10*4+0x200(zero)
	lw x11, 11*4+0x200(zero)
	lw x12, 12*4+0x200(zero)
	lw x13, 13*4+0x200(zero)
	lw x14, 14*4+0x200(zero)
	lw x15, 15*4+0x200(zero)
	lw x16, 16*4+0x200(zero)
	lw x17, 17*4+0x200(zero)
	lw x28, 28*4+0x200(zero)
	lw x29, 29*4+0x200(zero)
	lw x30, 30*4+0x200(zero)
	lw x31, 31*4+0x200(zero)
#else
	lw gp,   0*4+0x200(zero)
	lw x1,   1*4+0x200(zero)
	lw x2,   2*4+0x200(zero)
	// do not restore x3 (gp)
	lw x4,   4*4+0x200(zero)
	lw x5,   5*4+0x200(zero)
	lw x6,   6*4+0x200(zero)
	lw x7,   7*4+0x200(zero)
	lw x8,   8*4+0x200(zero)
	lw x9,   9*4+0x200(zero)
	lw x10, 10*4+0x200(zero)
	lw x11, 11*4+0x200(zero)
	lw x12, 12*4+0x200(zero)
	lw x13, 13*4+0x200(zero)
	lw x14, 14*4+0x200(zero)
	lw x15, 15*4+0x200(zero)
	lw x16, 16*4+0x200(zero)
	lw x17, 17*4+0x200(zero)
	lw x18, 18*4+0x200(zero)
	lw x19, 19*4+0x200(zero)
	lw x20, 20*4+0x200(zero)
	lw x21, 21*4+0x200(zero)
	lw x22, 22*4+0x200(zero)
	lw x23, 23*4+0x200(zero)
	lw x24, 24*4+0x200(zero)
	lw x25, 25*4+0x200(zero)
	lw x26, 26*4+0x200(zero)
	lw x27, 27*4+0x200(zero)
	lw x28, 28*4+0x200(zero)
	lw x29, 29*4+0x200(zero)
	lw x30, 30*4+0x200(zero)
	lw x31, 31*4+0x200(zero)
#endif

#endif // ENABLE_QREGS

	picorv32_retirq_insn()

.balign 0x200
irq_regs:
	// registers are saved to this memory region during interrupt handling
	// the program counter is saved as register 0
	.fill 32,4

	// stack for the interrupt handler
	.fill 128,4
irq_stack:


/* Main program
 **********************************/

start:
	/* zero-initialize all registers */

	addi x1, zero, 0
	addi x2, zero, 0
	addi x3, zero, 0
	addi x4, zero, 0
	addi x5, zero, 0
	addi x6, zero, 0
	addi x7, zero, 0
	addi x8, zero, 0
	addi x9, zero, 0
	addi x10, zero, 0
	addi x11, zero, 0
	addi x12, zero, 0
	addi x13, zero, 0
	addi x14, zero, 0
	addi x15, zero, 0
	addi x16, zero, 0
	addi x17, zero, 0
	addi x18, zero, 0
	addi x19, zero, 0
	addi x20, zero, 0
	addi x21, zero, 0
	addi x22, zero, 0
	addi x23, zero, 0
	addi x24, zero, 0
	addi x25, zero, 0
	addi x26, zero, 0
	addi x27, zero, 0
	addi x28, zero, 0
	addi x29, zero, 0
	addi x30, zero, 0
	addi x31, zero, 0

#ifdef ENABLE_HELLO
	/* set stack pointer */
	lui sp,(128*1024)>>12

	/* call hello C code */
	jal ra,hello
#endif

	/* running tests from riscv-tests */

#ifdef ENABLE_RVTST
#  define TEST(n) \
	.global n; \
	addi x1, zero, 1000; \
	picorv32_timer_insn(zero, x1); \
	jal zero,n; \
	.global n ## _ret; \
	n ## _ret:
#else
#  define TEST(n) \
	.global n ## _ret; \
	n ## _ret:
#endif

	TEST(lui)
	TEST(auipc)
	TEST(j)
	TEST(jal)
	TEST(jalr)

	TEST(beq)
	TEST(bne)
	TEST(blt)
	TEST(bge)
	TEST(bltu)
	TEST(bgeu)

	TEST(lb)
	TEST(lh)
	TEST(lw)
	TEST(lbu)
	TEST(lhu)

	TEST(sb)
	TEST(sh)
	TEST(sw)

	TEST(addi)
	TEST(slti) // also tests sltiu
	TEST(xori)
	TEST(ori)
	TEST(andi)
	TEST(slli)
	TEST(srli)
	TEST(srai)

	TEST(add)
	TEST(sub)
	TEST(sll)
	TEST(slt) // what is with sltu ?
	TEST(xor)
	TEST(srl)
	TEST(sra)
	TEST(or)
	TEST(and)

	TEST(mulh)
	TEST(mulhsu)
	TEST(mulhu)
	TEST(mul)

	TEST(div)
	TEST(divu)
	TEST(rem)
	TEST(remu)

	TEST(simple)

	/* set stack pointer */
	lui sp,(128*1024)>>12

	/* set gp and tp */
	lui gp, %hi(0xdeadbeef)
	addi gp, gp, %lo(0xdeadbeef)
	addi tp, gp, 0

#ifdef ENABLE_SIEVE
	/* call sieve C code */
	jal ra,sieve
#endif

#ifdef ENABLE_MULTST
	/* call multest C code */
	jal ra,multest
#endif

#ifdef ENABLE_STATS
	/* call stats C code */
	jal ra,stats
#endif

	/* print "DONE\n" */
	lui a0,0x10000000>>12
	addi a1,zero,'D'
	addi a2,zero,'O'
	addi a3,zero,'N'
	addi a4,zero,'E'
	addi a5,zero,'\n'
	sw a1,0(a0)
	sw a2,0(a0)
	sw a3,0(a0)
	sw a4,0(a0)
	sw a5,0(a0)


	//I add the test code here
	addi x0, x0, 0x0
addi x0, x0, 0x0
addi x0, x0, 0x0
XORI x11, x17, 1990
SLTU x27, x20, x11
SRL x2, x16, x13
SLL x31, x23, x8
XORI x29, x0, 1363
SLTIU x15, x21, 383
SRAI x1, x9, 19
SLLI x17, x22, 15
XOR x25, x21, x22
SLL x18, x17, x18
SRAI x8, x4, 7
XOR x31, x17, x2
SUB x27, x27, x20
SRAI x20, x22, 10
SLTU x17, x27, x23
SRA x11, x9, x1
SRLI x20, x29, 18
SLT x28, x18, x1
SLL x15, x12, x18
SLL x19, x7, x5
XOR x13, x21, x25
ADDI x30, x20, -1942
OR x1, x3, x7
SLTIU x25, x9, 1436
OR x16, x6, x30
ADD x11, x23, x25
XORI x28, x30, -1514
ADD x25, x10, x13
ADD x19, x5, x20
SLL x1, x5, x8
SRAI x8, x31, 27
SRAI x17, x24, 18
SLTIU x29, x26, 1272
SLTU x25, x12, x1
AND x7, x19, x19
SLLI x21, x25, 2
SLL x31, x22, x0
XORI x19, x11, -1473
AND x0, x5, x10
SLTU x11, x21, x24
SUB x16, x5, x4
SRLI x5, x17, 20
SRA x7, x18, x21
OR x14, x1, x26
SLTIU x6, x8, 925
ORI x9, x7, 76
ADDI x3, x7, -1464
SLL x7, x30, x23
SRLI x31, x0, 4
ADD x6, x8, x17
addi x0, x0, 0x0
addi x0, x0, 0x0
addi x0, x0, 0x0





	
	
	//IMPORTANT: DO NOT REMOVE OR CHANGE
	li a0, 0x20000000
	li a1, 123456789
	sw a1,0(a0)
	

	/* trap */
	ebreak


/* Hard mul functions for multest.c
 **********************************/

hard_mul:
	mul a0, a0, a1
	ret

hard_mulh:
	mulh a0, a0, a1
	ret

hard_mulhsu:
	mulhsu a0, a0, a1
	ret

hard_mulhu:
	mulhu a0, a0, a1
	ret

hard_div:
	div a0, a0, a1
	ret

hard_divu:
	divu a0, a0, a1
	ret

hard_rem:
	rem a0, a0, a1
	ret

hard_remu:
	remu a0, a0, a1
	ret

