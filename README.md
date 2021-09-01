# pyz80 - a Z80 cross assembler
Unofficial branch of https://sourceforge.net/projects/pyz80/ for fixes and enhancements.

[![Build Status](https://travis-ci.com/simonowen/pyz80.svg?branch=master)](https://app.travis-ci.com/github/simonowen/pyz80)

**pyz80 - a Z80 cross assembler**

Version 1.21, released 11 July 2013

By Andrew Collier

[https://www.intensity.org.uk/contact.html](https://www.intensity.org.uk/contact.html)

**Introduction**

pyz80 is an assembler for the assembly language of the Z80 micro-processor.

It is designed in particular for producing code to run on the Sam Coupé computer, and outputs disk images  which can be loaded by the SimCoupe emulator, or copied onto floppy disk for use with genuine hardware Sams. Nonetheless, it may be useful for users of other Z80-based platforms as well.

pyz80 is distributed under the terms of the [GNU General Public License](https://www.gnu.org/licenses/gpl.html). You can download and use it at no cost. See the file COPYING for more information.

**Installation**

pyz80 is written in python, and should work on MacOS X, Linux, Windows and other platforms if the appropriate interpreter is installed.

If you do not have python already, installers can be downloaded from:

[https://www.python.org/downloads/](https://www.python.org/downloads/)

**Usage**

pyz80 is a command-line tool. To use it, type pyz80 on your command line followed by the path to your input z80 source file:

e.g.        `pyz80 testing/test.z80s`

This will assemble the source file, and generate a disk image which contains the object code. You can supply more than one z80 source file, in which case each object file is saved as a separate file in the resulting disk image.

You can also add options (before the source files) to change details about the operation of pyz80:

`-o outputfile`

This option allows you to specify the name of the generated disk image. If this option is not given, the name is chosen based on the filename of the input source file (or the first input source file, if you have specified more than one).

`--nozip`

If this option is given, then the generated disk image will not be compressed. Otherwise, it will be compressed using gzip.

`-I filepath`

This option allows you to add an extra file to the disk image. It will be added to the directory before any assembled files, so for example you could add the "SAMDOS" file to the image to make it bootable.

You can add multiple files by using the -I option more than once:

e.g.        `pyz80 -I SAMDOS -I file.txt textReader.z80s`

Only code files can be added in this manner, they start at address 32768 and do not auto-execute. If you wish to change the start or execute address of the file, you will need to create a small Z80 source input file containing an MDAT directive. See the Syntax section for further details.

`--obj=outputfile`

This option allows you to save the generated code as a raw binary file, instead of part of a disk image. If you specify this option, no disk image will be generated (unless you also explicitly specify an output disk image file name).

You may only assemble a single input Z80 source file if you use this option.

```
-D symbol
-D symbol=value
```

This option defines a symbol before beginning to assemble the source file. The value of the symbol will be available to all expressions, both within instructions and also in assembler directives.

Since every symbol must have an integer value, if nothing is specified then 1 will be assumed.

`--exportfile=file`

This option allows you to save the whole symbol table to a file, following assembly.

Only one file can be exported in this fashion. The file format is likely to be specific to the version of python in use.

`--importfile=file`

This option allows you to import a symbol table which had previously been saved with the corresponding --exportfile option. All the symbols which had been defined during the previous assembly run, will be available to any part of your input Z80 source.

`--case`

If this option is given, then all symbols in the input Z80 source file will be treated as case sensitive (this is the behaviour of the original COMET assembler). Otherwise, any combination of lower case or upper case will be considered equivalent.

Please note this applies only to symbols. Instruction op-codes are always accepted in any combination of upper and lower case.

`--nobodmas`

If this option is given, then all expressions will be parsed from left to right instead of using the usual operator ordering rules, although brackets can still be used to specify precedence. For example the result of 10+10/10 in this mode will be two and not eleven (this is the behaviour of the original COMET assembler).

`--intdiv`

If this option is given, then all arithmetic divisions will give integer results, instead of floating point results. For example the result of 3/2 will be 1 and not 1.5 (this is the behaviour of the original COMET assembler). This will mostly affect calculations where an intermediate result is used for further calculations. The final value will always be truncated to an integer for register assignments.

`-s regexp`

This option allows you to print out the final value of one or more symbols at the end of assembling a source file. If you specify the text name of a particular symbol, pyz80 will print out the value of that symbol, and any others whose name completely contains what you have asked for:

e.g.        `pyz80 -s LDI3 testing/test.z80s`

prints        `{'LDI31': 33802, 'LDI3': 32850, 'LDI30': 33741, 'LDI32': 33865}`

Another common use is to print the value of every symbol in the whole assembly, by using the wild-card character (full stop):

e.g.        `pyz80 -s . testing/test.z80s`

Most precisely, regexp is a regular expression in python's format; if any part of a symbol matches the expression, then the symbol will be printed.

`-e`

If there are errors in the source code, pyz80 will attempt to diagnose the problem and tell you which line of the input Z80 source file is causing the problem. Occasionally, however, it can be difficult to see what mistake in that line is causing the confusion. If this option was specified on the command line, pyz80 will allow the python interpreter to print out its own messages about the problems it found, which may provide more detailed information.

**Syntax**

The input Z80 source text files have a format similar to that used by COMET, one of the Sam's most popular native assemblers.

Each line of the source file may contain one symbol definition, and one Z80 instruction or assembler directive.

Comments start with semicolon and continue to the end of the line.

**Instructions**

Z80 instructions and assembler directives may be formatted in upper or lower case.

e.g.
```
ld A,(DE)
INC e
```

pyz80 recognises all valid Z80 instructions, included those traditionally undocumented. In instructions where the low byte or high byte of the index registers can be addressed individually, they are referred to in pyz80 syntax as IXh, IXl, IYh and IYl.

The undocumented compound instructions (shift and rotate instructions which operate through the index registers and also copy the resulting value into a main register) have the following form of syntax in pyz80:

e.g.
```
ROT r, (IX+c)
```

Undocumented instruction SLL is also included, but because it doesn't operate as its name implies, pyz80 emits a warning when it is used. To assemble this instruction without a warning, use the opcode SL1 instead.

**Symbols**

Symbols are defined by the symbol name at the start of a line, followed by colon. They are generally given the address of the following instruction, but can be assigned explicitly using the EQU directive.

Symbols can contain any alphanumeric character, underscore, and full stop. Symbols formatted in upper or lower case may be used interchangeably, unless --case was specified on the command line.

General symbols have global scope. A symbol defined anywhere in the source is valid at all other points in the source, and must be defined only once.

A symbol starting with the @ sign (or consisting of the @ sign alone) is a local symbol. You may define a local symbol with the same name multiple times within the source, and this is not an error. The value of a local symbol is always taken from the a definition in the same file, the nearest definition to the point where the symbol is being used.

When using a local symbol, you can add + (or -) immediately following the @ sign, which forces pyz80 to use the next (or previous) definition respectively, always ignoring matches in the opposite direction.

e.g.
```
@loop:  call work
        dec b
        jr nz, @-loop ; jump up two lines
                
        ld b,7
@loop:  call office
        dec b
        jr nz, @loop
```

Where a pair of braces is used as part of a symbol name, the value of the expression inside will be substituted into the name of the symbol being defined or used.

e.g.
```
nine:     equ 9
k{nine}:  equ $ ; defines a symbol called k9
                ; is equivalent to  k9: equ $
```                

Note that the symbol being substituted must be available in the first pass of the assembler (i.e. it must be defined earlier in the file than it is used).

The expression defined (symbol) tests whether a symbol is defined anywhere in the source, without causing an error if it is not found. The value of this expression is always either 0, if the symbol does not exist, or 1, if it is defined no matter what its value. It can be particularly useful in conjunction with the command line option -D, which allows you to build variant code files without changing the source.

e.g.
```
ld a, defined(DEBUG)
```

**Assembler directives**

`ORG address`

Specify the origin of the code, i.e. the address from which it is intended to be run. This can be anywhere in the address range of the Z80, that is, 0 to 65535.

```
DUMP address
DUMP page, offset
```

Specify the destination address of the code output. This directive is available in two forms. The first takes an address from 16384 to 65535, these are addresses in pages 0 to 2 as addressed in BASIC. The second form takes a page number from 0 to 31, and an offset within that page of 0 to 16383.

`AUTOEXEC`

The current DUMP address will be marked as the execute address in the directory entry of the output disk image. When the code file is loaded from the disk image by SamDOS, it will automatically call the execute address. Note that when a machine code routine is called from BASIC it will usually be paged into section C of the address space.

This directive may not be used more than once during assembly.

```
DEFB  n [,n ...]
DB    n [,n ...]
```

Define bytes at the current address. Either DEFB or DB are allowed and are equivalent in meaning. n can be a literal number or any expression, in the range 0 to 255 (or -128 to +127).

```
DEFW  n [,n ...]
DW    n [,n ...]
```

Define words at the current address. Either DEFW or DW are allowed and are equivalent in meaning. n can be a literal number or any expression, in the range 0 to 65535 (or -32768 to +32767).

```
DEFM  "string"
DM    "string"
```

Define a message at the current address. The string is always delimited by double quotes. To include a double quote in the string itself, place two double quote characters adjacent to each other.

```
DEFS  n
DS    n
```

Define storage space at the current address. The current address increases by n bytes, thus leaving them available for your program's own use.

`DS ALIGN n`

This ensures that the following instruction will be aligned on the boundary specified, by leaving a space if necessary.

`MDAT "filename"`

This directive merges a data file from the host filesystem into the object code at the current address. filename is enclosed in double-quotes and is expressed relatively to the file currently being assembled.

```
INC "filename"
INCLUDE "filename"
```

This directive assembles the specified source file starting at the current address, as though the whole file were literally included in the current one. All symbols in the included file will be available globally, and must therefore be unique (unless they are local symbols).

(Both forms of this directive are equivalent, but INCLUDE is available to avoid confusion with the Z80's INC instruction)

`FOR range, instruction`

Repeats a single instruction (or directive) range times.

During assembly of this instruction, a symbol FOR is valid and holds the iteration number from 0 to range-1.

```
symbol: EQU FOR range
        ...
NEXT symbol
```

Repeats several lines of assembly, range times. When the lines between EQU FOR and NEXT are being assembled,  the symbol symbol is valid, and holds the iteration number from 0 to range-1.

FOR...NEXT blocks can be nested, with each layer using a different symbol name.

Where a local symbol is defined within a FOR...NEXT block, it can only be used within the same block. All references to it will target the same iteration.

```
IF expression
        ...
[ELSE IF expression]
        ...
[ELSE]
        ...
ENDIF
```

An IF block allows conditional assembly of your source based on some condition. For example, you may want to introduce some features during development of an application but to leave them out of release builds; in this case, IF blocks can be effectively used in conjunction with the -D command line option.

e.g.

```
IF defined (DEBUG)
  XOR A                
  OUT (CLUT),a
ENDIF
```

Note that any symbols used in the expression must be available in the first pass of the assembler (i.e. they must be defined earlier in the file than they are used).

`ASSERT condition`

This directive evaluates whether condition is true, and aborts assembly if not. For example, this can be used to ensure that the size of your code has not overstepped any limits you may be imposing.

`PRINT expression1[, expression2 ...]`

Prints the result of the expressions as soon as they are evaluated during assembly. Can be useful for logging and debugging, and showing the value of symbols (as an alternative to the -s command line option)

**Expressions and special characters**

Wherever an instruction or directive requires a number, a mathematical expression can be used instead. These are allowed to contain any symbol names defined in the file. If the result of an expression is negative, it will appear in the instruction in two's complement.

`$`   a symbol representing the address of the current instruction  
`&`   prefixes a hexadecimal number  
`0x`  prefixes a hexadecimal number  
`%`   prefixes a binary number  
`0b`  prefixes a binary number  
`"`   a single character enclosed in double-quotes can be used to represent the ascii value of that character  
`""`  strings are delimited by the double-quote character. To encode a literal double-quote within a string, use the double-quote character twice.  
`\`   mod

Several mathematical functions are available within expressions. You may use any method of the random or math python modules; a few examples are listed below:

`random()`

Returns a random floating point number between 0 and 1. It should be noted that while intermediate stages of the calculation are allowed to have non-integer values, the final value of an expression is always rounded to the nearest integer. Thus it can be useful to multiply float numbers by a constant to keep them in a useful range:

e.g.
```
DEFB random()\*256
```

`randrange(start,stop [,step])`

Returns a random integer in the range start ≤ x < stop

```
sin(angle)
cos(angle)
```

angle is specified in radians.

`pi`

**Thanks**

Thanks to Edwin Blink for writing the original COMET assembler for the Sam Coupé.

Thanks to Simon Owen and other users for their feedback during development.

**Links**

pyz80 web page:

[https://www.intensity.org.uk/samcoupe/pyz80.html](https://www.intensity.org.uk/samcoupe/pyz80.html)

SimCoupe Homepage:

[http://www.simcoupe.org/](http://www.simcoupe.org/)

World of Sam archive:

[https://www.worldofsam.org/](https://www.worldofsam.org/)

Wikipedia entry for the SAM Coupé (and for more links):

[https://wikipedia.org/wiki/Sam\_Coupe](https://wikipedia.org/wiki/SAM_Coupé)

**Disclaimer**

THIS PROGRAM AND DOCUMENTATION ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, NOT EVEN THE IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.  BY USING THE PROGRAM, YOU AGREE TO BEAR ALL RISKS AND LIABILITIES ARISING FROM THE USE OF THE PROGRAM AND DOCUMENTATION AND THE INFORMATION PROVIDED BY THE PROGRAM AND THE DOCUMENTATION.

**Release History**

Version 1.21, 11 July 2013

  - A symbol name could include tab characters, which should be treated as a source error (reported by Chris Pile)

Version 1.2, 2 February 2009

  - Add PRINT directive
  - Local symbols used in an included file will search the parent file to find a definition
  - Chooses more appropriate names for files on the Sam disk image, based on the input source filename (reported by Thomas Harte)
  - Fixed options --obj and -o were incorrectly conflicting (reported by Thomas Harte)
  - Fixed symbol names containing strings 0b and 0x were misparsed (fixed by Simon Owen)
  - Fixed a misparseing of incorrect instructions of the form LD H,(23) (reported by Thomas Harte)

Version 1.1, 13 April 2007

  - Fix a problem when the comma character is included in quoted expressions
  - Documentation fix for INCLUDE directive

Version 1.0, 10 April 2007

  - option to include other files on the resulting disk image, or multiple object files
  - IXh, IXl, IYh and IYl can be used in operands where this forms a valid (undocumented) instruction
  - fixed ex (sp),ix
  - fixed parse bug if a symbol name starts with IX or IY
  - support for "compound" instructions such as RLC r,(IX+c)
  - option to not gzip the disk image
  - option to save raw binaries and not just into disk images
  - option to treat labels as case sensitive (as COMET itself does)
  - option to work without bodmas operator precedence (as COMET itself does)
  - better package with documentation and test sources
  - local" symbols starting with the @ character do not need to be unique; use them for the beginning of loops, for example. Any references to them will go to the nearest in the same file (or use @+ and @- for always the next or previous respectively)
  - IF, ELSE (IF), ENDIF pseudo-opcodes
  - defined(symbol) tests whether a symbol exists
  - multi-line FOR constructs for repeating sequences of instructions
  - curly braces text-substitute the value of one symbol into the name of another,
  - option to predefine symbols from the pyz80 command line
  - option to save and load whole symbol tables
  - saved files include only used space, and not the rest of the page

Version 0.6, 10 February 2006

  - implemented SLL (with a warning)
  - use directive AUTOEXEC (usually straight after a DUMP) to set automatic execution of code from the current target address
  - simple test to stop output file overwriting source file
  - instructions may now be tab separated, not just space
  - add warning when operands are generated out of range of the instruction
  - better default output file name
  - cope better with errors in z80s source (symbol names used twice)
  - added -e option (lets you see python's error messages directly)
  - allow . in symbol names
  - file doesn't have to start at page boundary (helpful for writing boot sectors and stuff)

Version 0.5, 15 January 2005

  - new pseudo-opcode: FOR limit, codeseq
  - allow % as a prefix to binary numbers
  - fix LD (IX+n),n
  - slightly more flexibility if EQU definition depends on a symbol has not been defined until later in the source file (this is not allowed to affect code size)
  - allow leading zeros in decimal literals (passing these directly to the python expression parser as previously would cause them to be treated as octal)
  - allow DB, DW ... as shorthand forms of DEFB, DEFW etc
  - allow character constants expressions (e.g. DB "A")
  - save file correctly if unused part of the last sector falls out of memory
  - more robust expression parser doesn't replace substrings of symbols
  - DEFM can cope with strings containing semicolons, colons
  - import python math and random modules to make some of its functions available to the expression parser
  - removed nesting of functions because the scoping rules don't seem to work the way FOR needs them
  - fixed confusion between INC opcode and INC (include) directive
  - changed file loading slightly because fileinput doesn't cut the recursive mustard.
  - allow underscore character in symbol names, and sanity check for syntax errors
  - print a subset of the symbol table after assembly is complete
  - files included by files included along a relative path will search for their files on that path

Version 0.1, 19 November 2004

  - initial release
