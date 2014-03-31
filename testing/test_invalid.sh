#!/bin/sh

LINES=`grep -E "^\s*[^;]+" invalid.z80s | wc -l`
LINE=1

grep -E "^\s*[^;]+" invalid.z80s | while read -r line ; do
    LINE=$(( $LINE + 1))

    cat << EOF > _test_.asm
nn: equ &1122
n:  equ &33
o:  equ &44

    $line
EOF
    ../pyz80.py --obj=_test_.bin _test_.asm 2>&1 > /dev/null
    if [ $? -eq 0 ]; then
        echo -n "\rBUG:  $line  assembles to  "
        od -tx1 _test_.bin | head -1 | cut -d" " -f2- | tr a-f A-F
    else
        echo -n "\r$(( $LINE * 100 / $LINES ))%"
    fi
done

echo
rm -f _test_.asm _test_.bin
