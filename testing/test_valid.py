# Test valid code assembles correctly

import os
import sys
import gzip
import tempfile
import subprocess

curr_dir = os.path.split(__file__)[0]
pyz80_path = os.path.join(curr_dir, '../pyz80.py')

test_files = [
    ("golden.z80s", "golden.dsk.gz", "golden.bin", ["--nozip"]),
    ("golden.z80s", "golden.dsk.gz", "golden.bin", []),
    ("valid.z80s", None, "valid.bin", []),
]


def compare_files( output_path, expected_path ):
    with open(output_path, 'rb') as f1, open(expected_path, 'rb') as f2:
        output = bytearray(f1.read())
        expected = f2.read()

    if output.startswith(b'\x1f\x8b'):
        output = bytearray(gzip.decompress( output ))

    if expected.startswith(b'\x1f\x8b'):
        expected = gzip.decompress( expected )

    if '.dsk' in expected_path:
        for slot in range(18):
            offset = (slot * 256) + 245  # file date
            output[offset:offset+5] = expected[offset:offset+5]  # ignore dates

    return output == expected


def assemble_file( asm_file, dsk_file, bin_file, extra_opts ):
    exitcode = 0

    asm_path = os.path.join( curr_dir, asm_file )
    dsk_path = os.path.join( curr_dir, dsk_file ) if dsk_file else None
    bin_path = os.path.join( curr_dir, bin_file ) if bin_file else None

    with tempfile.NamedTemporaryFile(suffix=".dsk", delete=False) as dskfile:
        dsk_out_path = dskfile.name

    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as binfile:
        bin_out_path = binfile.name

    try:
        result = subprocess.run(
            [ "python", pyz80_path, *extra_opts, '-o', dsk_out_path, '--obj', bin_out_path, asm_path ],
            capture_output=True,
            text=True )

        if result.returncode != 0:
            print( f"ERROR: '{asm_file}' failed to assemble: {result.stderr}", file=sys.stderr )
        else:
            if dsk_path and not compare_files( dsk_out_path, dsk_path  ):
                print( f"ERROR: '{asm_file}' disk image mismatch against '{dsk_file}'", file=sys.stderr )
                exitcode = 1

            if bin_path and not compare_files( bin_out_path, bin_path ):
                print( f"ERROR: '{asm_file}' binary output mismatch against '{bin_file}'", file=sys.stderr )
                exitcode = 1
    finally:
        if os.path.isfile( dsk_out_path ):
            os.remove( dsk_out_path )
        if os.path.isfile( bin_out_path ):
            os.remove( bin_out_path )

    return exitcode


if __name__ == "__main__":
    exitcode = 0
    for asm_file, dsk_file, bin_file, extra_opts in test_files:
        exitcode |= assemble_file( asm_file, dsk_file, bin_file, extra_opts )

    sys.exit( exitcode )
