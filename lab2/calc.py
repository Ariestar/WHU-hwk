#!/usr/bin/env python3
"""
Relocation calculation verification script for Lab 2
Based on CS:APP Chapter 7 Figure 7.10 algorithm.
"""

def verify_relocation(name, symbol_name, addr_sym, addend, refaddr, expected_disp):
    calc_disp = addr_sym + addend - refaddr
    calc_disp_u32 = calc_disp & 0xFFFFFFFF
    print(f"=== {name} ({symbol_name}) ===")
    print(f"  ADDR(r.symbol)   = 0x{addr_sym:x}")
    print(f"  r.addend         = {addend} (0x{addend & 0xFFFFFFFF:x})")
    print(f"  refaddr          = 0x{refaddr:x}")
    print(f"  Calculation      = 0x{addr_sym:x} + ({addend}) - 0x{refaddr:x}")
    print(f"                   = 0x{calc_disp:x} (32-bit: 0x{calc_disp_u32:08x})")
    print(f"  Expected disp    = 0x{expected_disp:x}")
    print(f"  Match?           = {'PASS' if calc_disp == expected_disp else 'FAIL'}\n")

print("--------------------------------------------------")
print("1. PIE Mode (prog: gcc -Og -o prog main.c sum.c)")
print("--------------------------------------------------")
# ADDR(main) = 0x1129
# array ref: offset in main = 0x10 -> refaddr = 0x1129 + 0x10 = 0x1139
# ADDR(array) = 0x4010, addend = -4
verify_relocation(
    "PC-Relative Relocation for array",
    "array",
    addr_sym=0x4010,
    addend=-4,
    refaddr=0x1139,
    expected_disp=0x2ed3
)

# sum ref: offset in main = 0x15 -> refaddr = 0x1129 + 0x15 = 0x113e
# ADDR(sum) = 0x1150, addend = -4
verify_relocation(
    "PC-Relative Relocation for sum",
    "sum",
    addr_sym=0x1150,
    addend=-4,
    refaddr=0x113e,
    expected_disp=0x0e
)

print("--------------------------------------------------")
print("2. Non-PIE Mode (prog_nopie: gcc -Og -no-pie)")
print("--------------------------------------------------")
# ADDR(main) = 0x401106
# array ref: offset in main = 0x10 -> refaddr = 0x401106 + 0x10 = 0x401116
# ADDR(array) = 0x404010, addend = -4
verify_relocation(
    "PC-Relative Relocation for array",
    "array",
    addr_sym=0x404010,
    addend=-4,
    refaddr=0x401116,
    expected_disp=0x2ef6
)

# sum ref: offset in main = 0x15 -> refaddr = 0x401106 + 0x15 = 0x40111b
# ADDR(sum) = 0x401130, addend = -4
verify_relocation(
    "PC-Relative Relocation for sum",
    "sum",
    addr_sym=0x401130,
    addend=-4,
    refaddr=0x40111b,
    expected_disp=0x11
)

print("--------------------------------------------------")
print("3. Non-PIE Absolute Relocation (prog_nopie_abs: -fno-pie)")
print("--------------------------------------------------")
# Absolute reference: *refptr = ADDR(symbol) + addend
addr_array = 0x404010
addend = 0
abs_val = addr_array + addend
print(f"=== Absolute Relocation (R_X86_64_32 array) ===")
print(f"  ADDR(array)      = 0x{addr_array:x}")
print(f"  r.addend         = {addend}")
print(f"  Calculation      = 0x{addr_array:x} + {addend} = 0x{abs_val:x}")
print(f"  Expected in code = 0x404010 (mov $0x404010, %edi)")
print(f"  Match?           = {'PASS' if abs_val == 0x404010 else 'FAIL'}")
