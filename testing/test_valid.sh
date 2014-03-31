#!/bin/sh

if [ ! -f valid.bin ]; then
    pasmo --bin valid.z80s valid.bin

    if [ $? -ne 0 ]; then
        echo "Pasmo needed to build comparison output."
        exit 1
    fi
fi

../pyz80.py --obj=_test_.bin valid.z80s 2>&1 >/dev/null

if [ $? -eq 0 ]; then
    cmp _test_.bin valid.bin 2>&1 >/dev/null

    if [ $? -eq 0 ]; then
        echo "All valid Z80 instructions are correct!"
    else
        echo "Output doesn't match!  Compare _test_.bin and valid.bin."
        exit 1
    fi
fi

rm -f _test_.bin
