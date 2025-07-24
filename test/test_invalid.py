# Test invalid instructions do not assemble

import os
import sys
import tempfile
import subprocess

curr_dir = os.path.split(__file__)[0]
pyz80_path = os.path.join(curr_dir, '../src/pyz80/pyz80.py')

equs = '\n'.join(["nn: equ &1122", "n: equ &33", "o: equ &44"]) + '\n'

test_sets = [
    ("and ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("or ",        ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("xor ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("cp ",        ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("add a",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("adc a",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("sbc a,",     ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("sub ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("add hl",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","c","d","e","h","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r"]),
    ("adc hl,",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","c","d","e","h","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r"]),
    ("sbc hl,",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","c","d","e","h","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r"]),
    ("rl ",        ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("rlc ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("rr ",        ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("rrc ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("sla ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("sll ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("sra ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("srl ",       ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("bit 0,",     ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("set 0,",     ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("res 0,",     ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("ex (sp),",   ["(bc)","(de)","(hl)","(ix)","(ix+o)","(nn)","a","af","af'","b","bc","c","d","de","e","h","i","ixh","ixl","iyh","iyl","l","n","r","sp"]),
    ("ex af,",     ["(bc)","(de)","(hl)","(ix)","(iy+o)","(nn)","a","af","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ex de,",     ["(bc)","(de)","(hl)","(ix)","(iy+o)","(nn)","a","af","af'","b","bc","c","d","de","e","h","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ex hl,",     ["de"]),
    ("inc ",       ["(bc)","(de)","(nn)","af","af'","i","n","r"]),
    ("dec ",       ["(bc)","(de)","(nn)","af","af'","i","n","r"]),
    ("push ",      ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af'","b","c","d","e","h","i","ixh","ixl","iyh","iyl","l","n","r","sp"]),
    ("pop ",       ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af'","b","c","d","e","h","i","ixh","ixl","iyh","iyl","l","n","r","sp"]),
    ("in a,",      ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("in b,",      ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("out (c),",   ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","n","r","sp"]),
    ("out (n),",   ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","r","sp"]),
    ("jp ",        ["(bc)","(de)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","r","sp"]),
    ("jr ",        ["m,$","p,$","pe,$","po,$"]),
    ("ld a,",      ["af","af'","bc","de","hl","ix","iy","sp"]),
    ("ld b,",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("ld c,",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("ld d,",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("ld e,",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","iy","r","sp"]),
    ("ld h,",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","r","sp"]),
    ("ld l,",      ["(bc)","(de)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","r","sp"]),
    ("ld af,",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ld af',",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ld hl',",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ld bc,",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","r","sp"]),
    ("ld de,",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","r","sp"]),
    ("ld hl,",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","r","sp"]),
    ("ld ix,",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","r","sp"]),
    ("ld iy,",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","a","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","r","sp"]),
    ("ld ixh,",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","h","hl","i","ix","iy","l","r","sp"]),
    ("ld ixl,",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","h","hl","i","ix","iy","l","r","sp"]),
    ("ld iyh,",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","h","hl","i","ix","iy","l","r","sp"]),
    ("ld iyl,",    ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","h","hl","i","ix","iy","l","r","sp"]),
    ("ld sp,",     ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","a","af","af'","b","bc","c","d","de","e","h","i","ixh","ixl","iyh","iyl","l","r","sp"]),
    ("ld i,",      ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ld r,",      ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ld (bc),",   ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ld (de),",   ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","b","bc","c","d","de","e","h","hl","i","ix","ixh","ixl","iy","iyh","iyl","l","n","r","sp"]),
    ("ld (nn),",   ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","b","c","d","e","h","i","ixh","ixl","iyh","iyl","l","n","r"]),
    ("ld (hl),",   ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","r","sp"]),
    ("ld (ix+o),", ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","r","sp"]),
    ("ld (iy+o),", ["(bc)","(de)","(hl)","(ix+o)","(iy+o)","(nn)","af","af'","bc","de","hl","i","ix","ixh","ixl","iy","iyh","iyl","r","sp"]),
    ("ld ",        ["(ix-129),n", "(ix+128),n", "(iy-129),n", "(iy+128),n"]),
    ("im ",        ["-1","3"]),
    ("rst ",       ["-1","&01","&100","&37","&40","&f0","&ff"]),
]


def assemble_instr(line):
    exitcode = 0

    with tempfile.NamedTemporaryFile(suffix=".asm", delete=False, mode='w+t') as asm_file:
        asm_file.write(equs)
        asm_file.write(line)
        asm_path = asm_file.name

    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as bin_file:
        bin_path = bin_file.name

    try:
        result = subprocess.run(
            ["python", pyz80_path, '--obj', bin_path, '-o', os.devnull, asm_path],
            capture_output=True,
            text=True)

        if result.returncode == 0:
            with open(bin_path, 'rb') as f:
                content = f.read()
            print(f"BUG: '{line.strip().upper()}' assembles to: {content.hex().upper()}", file=sys.stderr)
            exitcode = 1

    finally:
        if os.path.isfile(asm_path):
            os.remove(asm_path)
        if os.path.isfile(bin_path):
            os.remove(bin_path)

    return exitcode


def main():
    exitcode = 0
    for prefix, operands in test_sets:
        for op in operands:
            instr = f" {prefix}{op}"
            exitcode |= assemble_instr(instr)
    sys.exit(exitcode)


if __name__ == "__main__":
    main()
