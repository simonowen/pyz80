import os
import subprocess
import re
import sys
import binascii

exitcode = 0
equ = '\n'.join( [ "nn: equ &1122", "n: equ &33", "o: equ &44", "", "" ] )

file = open( "invalid.z80s", "r" )
for line in file:

	if line.strip() and not re.match( ".*;.*", line ):
			
		print( "assembling", line )
		asm = open( "_test_.asm", "w" )
		asm.write( equ )
		asm.write( line )
		asm.close()
		subprocess.call( [ "python", "../pyz80.py", "--obj=_test_.bin", "_test_.asm" ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
		
		if os.path.isfile( "_test_.bin" ):
		
			exitcode = 1
			with open("_test_.bin", 'rb') as f:
				content = f.read()			
			print( "BUG:", line.strip(), "assembles to", binascii.hexlify( content ) )
			os.remove( "_test_.bin" )			
		
if os.path.isfile( "_test_.asm" ):
	os.remove( "_test_.asm" )
file.close()	

sys.exit( exitcode )