#!/usr/bin/env python

def printusage():
    print "pyz80 by Andrew Collier, version 0.6+ Mar-2007"
    print "http://www.intensity.org.uk/samcoupe/pyz80.html"
    print "Usage:"
    print "     pyz80 (options) inputfile"
    print "Options:" 
    print "-o outputfile"
    print "   save the resulting disk image at the given path"
    print "-s regexp"
    print "   print the value of any symbols matching the given regular expression"
    print "   This may be used multiple times to output more than one subset"
    print "--nozip"
    print "   do not compress the resulting disk image"
    print "-e"
    print "   use python's own error handling instead of trying to catch parse errors"
    print "--case"
    print "   treat source labels as case sensitive (as COMET itself did)"
    print "-D symbol=value"
    print "   Define a symbol before parseing the source"
    print "   (value is integer; if omitted, assume 1)"

def printlicense():
    print "This program is free software; you can redistribute it and/or modify"
    print "it under the terms of the GNU General Public License as published by"
    print "the Free Software Foundation; either version 2 of the License, or"
    print "(at your option) any later version."
    print " "
    print "This program is distributed in the hope that it will be useful,"
    print "but WITHOUT ANY WARRANTY; without even the implied warranty of"
    print "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the"
    print "GNU General Public License for more details."
    print " "
    print "You should have received a copy of the GNU General Public License"
    print "along with this program; if not, write to the Free Software"
    print "Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA"

# CHANGELOG

# changes since last release
#
# - IXh, IXl, IYh and IYl can be used in operands where this forms a valid (undocumented) instruction
# - option to not gzip the disk image
# - option to treat labels as case sensitive (as COMET itself does)
# - better package with documentation and test sources

# version 0.6 10-Feb-2006
#
# - implemented SLL (with a warning)
# - use directive AUTOEXEC (usually straight after a DUMP) to set automatic execution of code from the current target address
# - simple test to stop output file overwriting source file
# - instructions may now be tab separated, not just space
# - add warning when operands are generated out of range of the instruction
# - better default output file name
# - cope better with errors in z80s source (symbol names used twice)
# - added -e option (lets you see python's error messages directly)
# - allow . in symbol names
# - file doesn't have to start at page boundary (helpful for writing boot sectors and stuff)

# version 0.5 15-Jan-2005
#
# - new pseudo-opcode: FOR limit, codeseq
#   repeats an instruction multiple times
#   symbol FOR takes value of 0 ... limit-1
#   eg FOR 128, LDI
#      FOR 256, DEFB -0.5+127.5*sin((FOR/256.0)*pi*2)
# - allow % as a prefix to binary numbers
# - fix LD (IX+n),n
# - slightly more flexibility if EQU definition depends on a symbol has not been defined
#   until later in the source file (this is not allowed to affect code size)
# - allow leading zeros in decimal literals (passing these directly to the python
#   expression parser as previously would cause them to be treated as octal)
# - allow DB, DW ... as shorthand forms of DEFB, DEFW etc
# - allow character constants expressions (e.g. DB "A")
# - save file correctly if unused part of the last sector falls out of memory
# - more robust expression parser doesn't replace substrings of symbols
# - DEFM can cope with strings containing semicolons, colons
# - import python math and random modules to make some of its functions available to the expression parser
# - removed nesting of functions because the scoping rules don't seem to work the way FOR needs them
# - fixed confusion between INC opcode and INC (include) directive
# - changed file loading slightly because fileinput doesn't cut the recursive mustard.
# - allow underscore character in symbol names, and sanity check for syntax errors
# - print a subset of the symbol table after assembly is complete
# - files included by files included along a relative path will search for their files on that path

# version 0.1 19-Nov-2004
#
# - initial release

# KNOWN ISSUES
# -  quoted commas, in lines where other commas are expected
#    eg. DEFB 43,23,",",17,56
#    I don't think this occurs very often.

# PLANNED CHANGES BEFORE VERSION 1.0
# 
# - option to include other files on the resulting disk image
# - support for "compound" instructions such as RLC r,(IX+c)
# - IF, ELSE (IF), ENDIF pseudo-opcodes


import getopt
import sys
import array
import fileinput
import re
import gzip
import math # for use by expressions in source files
import random

def make_disk_image(memory, outputfile):
    global firstpageoffset
    
    image = array.array('B')
    image.append(0)
    targetsize = 80*10*2*512
    # disk image is arranged as: tr 0 s 1-10, tr 128 s 1-10, tr 1 s 1-10, tr 128 s 1-10 etc
    
    while len(image) < targetsize:
        image.extend(image)
    while len(image) > targetsize:
        image.pop()
    
    firstusedpage = ''
    lastusedpage = ''
    
    for i in range(32):
        if memory[i]!='':
            if firstusedpage == '':
                firstusedpage = i
            lastusedpage = i
    
    if firstusedpage!='':
        filelength = (lastusedpage - firstusedpage + 1) * 16384
        
        if firstpage == firstusedpage:
            filelength -= firstpageoffset
        else:
            firstpageoffset = 0
        
        image[0] = 19 # code file
        
        if (autoexecpage>0) :
            
            image[1] = ord('A')
            image[2] = ord('U')
            image[3] = ord('T')
            image[4] = ord('O')
            
            for i in range(4):
                if i < len(outputfile):
                    image[5+i] = ord(outputfile[i])
                else:
                    image[5+i] = ord(' ')
        
        else:
            
            for i in range(8):
                if i < len(outputfile):
                    image[1+i] = ord(outputfile[i])
                else:
                    image[1+i] = ord(' ')
        
        image[9]  = ord('.')
        image[10] = ord('O') # filename
        
        nsectors = (filelength+9)/510
        image[11] = nsectors / 256 # MSB number of sectors used
        image[12] = nsectors % 256 # LSB number of sectors used
        
        image[13] = 4 # starting track
        image[14] = 1 # starting sector
    
    # 15 - 209 sector address map
    # 210-219 MGT future and past (reserved)
        
        image[220] = 0 # flags (reserved)
    
    # 221-231 File type information (n/a for code files)
    # 232-235 reserved
        
        image[236] = firstusedpage # start page number
        image[237] = (firstpageoffset%256) # page offset (in section C, 0x8000 - 0xbfff)
        image[238] = 128 + (firstpageoffset / 256)
        
        image[239] = filelength/16384 # pages in length
        image[240] = filelength%256 # file length % 16384
        image[241] = (filelength%16384)/256
        
        if (autoexecpage>0) :
            image[242] = autoexecpage # execution address or 255 255 255 (basicpage, L, H - offset in page C)
            image[243] = autoexecorigin % 256;
            image[244] = (autoexecorigin%16384)/256 + 128
        else:
            image[242] = 255 # execution address or 255 255 255 (basicpage, L, H - offset in page C)
            image[243] = 255
            image[244] = 255
    
    # write table of used sectors (can precalculate from number of used bits)
        i=15
        while nsectors > 0:
            if nsectors>7:
                image[i]=0xff
                nsectors -= 8
            else:
                image[i] = (1 << nsectors) -1
                nsectors=0
            i += 1
        
        side = 0
        track = 4
        sector = 1
        fpos = 0
    
    # write file's 9 byte header and file
        imagepos = (track*20+side*10+(sector-1))*512
    # 0       File type               19 for a code file
        image[imagepos + 0] = 19
    # 1-2     Modulo length           Length of file % 16384
        image[imagepos + 1] = filelength%256
        image[imagepos + 2] = (filelength%16384)/256
    # 3-4     Offset start            Start address
        image[imagepos + 3] = (firstpageoffset%256)
        image[imagepos + 4] = 128 + (firstpageoffset / 256)
    # 5-6     Unused
    # 7       Number of pages
        image[imagepos + 7] = filelength/16384
    # 8       Starting page number
        image[imagepos + 8] = firstusedpage
        
        while fpos < filelength:
            imagepos = (track*20+side*10+(sector-1))*512
            unadjustedimagepos = imagepos
            if side==0 and track==4 and sector==1:
                copylen = 501
                imagepos += 9
            else:
                if (filelength-fpos) > 509:
                    copylen = 510
                else:
                    copylen = (filelength-fpos)
            
            if ((fpos+firstpageoffset)/16384) == (((fpos+firstpageoffset)+copylen-1)/16384):
                if memory[firstusedpage+(fpos+firstpageoffset)/16384] != '':
                    image[imagepos:imagepos+copylen] = memory[firstusedpage+(fpos+firstpageoffset)/16384][(fpos+firstpageoffset)%16384 : (fpos+firstpageoffset)%16384+copylen]
            else:
                copylen1 = 16384 - ((fpos+firstpageoffset)%16384)
                page1 = (firstusedpage+(fpos+firstpageoffset)/16384)
                if memory[page1] != '':
                    image[imagepos:imagepos+copylen1] = memory[page1][(fpos+firstpageoffset)%16384 : ((fpos+firstpageoffset)%16384)+copylen1]
                if (page1 < 31) and memory[page1+1] != '':
                    image[imagepos+copylen1:imagepos+copylen] = memory[page1+1][0 : ((fpos+firstpageoffset)+copylen)%16384]
            
            fpos += copylen
            
            sector += 1
            if sector == 11:
                sector = 1
                track += 1
                if track == 80:
                    track = 0
                    side += 1
            
            # pointers to next sector and track
            if (fpos < filelength):
                image[unadjustedimagepos+510] = track + 128*side
                image[unadjustedimagepos+511] = sector
    
    imagestr = image.tostring()
    if ZIP:
        dskfile = gzip.open(outputfile, 'wb')
    else:
        dskfile = open(outputfile, 'wb')
    dskfile.write(imagestr)
    dskfile.close()
    
    
    

def warning(message):
    print 'Warning:', message
    print global_currentfile,'"'+global_currentline.strip()+'"'

def fatal(message):
    print 'Error:', message
    print global_currentfile,'"'+global_currentline.strip()+'"'
    sys.exit(1)

def parse_expression(arg, signed=0, byte=0, word=0, silenterror=0):
    if ',' in arg:
        if silenterror:
            return ''
        fatal("Erroneous comma in expression"+arg)
    
    while 1:
    	match = re.search('"(.)"', arg)
        if match:
            arg = arg.replace('"'+match.group(1)+'"',str(ord(match.group(1))))
        else:
            break
    
    arg = arg.replace('$','('+str(origin)+')')
    arg = arg.replace('%','0b') # COMET syntax for binary literals (parsed later, change to save confusion with modulus)
    arg = arg.replace('\\','%') # COMET syntax for modulus
    arg = arg.replace('&','0x') # COMET syntax for hex numbers
    
    arg = arg.replace('0X','0x') # darnit, this got capitalized
    arg = arg.replace('0B','0b') # darnit, this got capitalized
            

# if the argument contains letters at this point,
# it's a symbol which needs to be replaced
    
    testsymbol=''
    argcopy = ''
    for c in arg+' ':
        if c.isalnum() or c=="_" or c==".":
            testsymbol += c
        else:
            if (testsymbol != ''):
                if not testsymbol[0].isdigit():
                    if (symboltable.has_key(testsymbol)):
                        testsymbol = str(symboltable[testsymbol])
                    else:
                        understood = 0
                        # some of python's math expressions should be available to the parser
                        if not understood:
                            parsestr = 'math.'+testsymbol.lower()
                            try:
                                eval(parsestr)
                                understood = 1
                            except:
                                understood = 0
                        
                        if not understood:
                            parsestr = 'random.'+testsymbol.lower()
                            try:
                                eval(parsestr)
                                understood = 1
                            except:
                                understood = 0
                        
                        if not understood:
                            if silenterror:
                                return ''
                            fatal("Error in expression "+arg+": Undefined symbol "+testsymbol)
                        
                        testsymbol = parsestr
                elif testsymbol[0]=='0' and len(testsymbol)>2 and testsymbol[1]=='b':
                # binary literal
                    literal = 0
                    for digit in testsymbol[2:]:
                        literal *= 2
                        if digit == '1':
                            literal += 1
                    testsymbol = str(literal)
                
                elif testsymbol[0]=='0' and len(testsymbol)>1 and testsymbol[1]!='x':
                # literals with leading zero would be treated as octal,
                # COMET source files do not expect this
                    decimal = testsymbol
                    while decimal[0] == '0' and len(decimal)>1:
                        decimal = decimal[1:]
                    testsymbol = decimal
                
                argcopy += testsymbol
                testsymbol = ''
            argcopy += c
    
    farg = eval(argcopy)
    if farg >= -.5:
        farg += 0.5
    else:
        farg -= 0.5
    narg = int(farg)
#    print arg, " -> ",argcopy," == ",narg
    
    if signed:
        if byte:
            if (  -128 < narg > 127):
                warning ("Signed byte value truncated from "+str(narg));
            narg = (narg + 128)%256 -128
        elif word:
            if (  -32768 < narg > 32767):
                warning ("Signed word value truncated from "+str(narg));
            narg = (narg + 32768)%65536 - 32768
    else:
        if byte:
            if (  0 < narg > 255):
                warning ("Unsigned byte value truncated from "+str(narg));
            narg %= 256
        elif word:
            if (  0 < narg > 65535):
                warning ("Unsigned byte value truncated from "+str(narg));
            narg %= 65536
    return narg

def double(arg, allow_af_instead_of_sp=0, allow_af_alt=0, allow_index=1):
# decode double register [bc, de, hl, sp][ix,iy] --special:  af af'
    double_mapping = {'BC':([],0), 'DE':([],1), 'HL':([],2), 'SP':([],3), 'IX':([0xdd],2), 'IY':([0xfd],2), 'AF':([],5), "AF'":([],4) }
    rr = double_mapping.get(arg.strip().upper(),([],''))
    if (rr[1]==3) and allow_af_instead_of_sp:
        rr = ([],'')
    if rr[1]==5:
        if allow_af_instead_of_sp:
            rr = ([],3)
        else:
            rr = ([],'')
    if (rr[1]==4) and not allow_af_alt:
        rr = ([],'')
    
    if (rr[0] != []) and not allow_index:
        rr = ([],'')
    
    return rr

def single(arg, allow_i=0, allow_r=0, allow_index=1, allow_offset=1, allow_half=1):
#decode single register [b,c,d,e,h,l,(hl),a][(ix {+c}),(iy {+c})]
    single_mapping = {'B':0, 'C':1, 'D':2, 'E':3, 'H':4, 'L':5, 'A':7, 'I':8, 'R':9, 'IXH':10, 'IXL':11, 'IYH':12, 'IYL':13 }
    m = single_mapping.get(arg.strip().upper(),'')
    prefix=[]
    postfix=[]
    
    if m==8 and not allow_i:
        m = ''
    if m==9 and not allow_r:
        m = ''
 
    if allow_half:
        if m==10:
            prefix = [0xdd]
            m = 4
        if m==11:
            prefix = [0xdd]
            m = 5
        if m==12:
            prefix = [0xfd]
            m = 4
        if m==13:
            prefix = [0xfd]
            m = 5
    else:
        if m >= 10 and m <= 13:
            m = '' 
    
    if m=='' and re.search("\A\s*\(\s*HL\s*\)\s*\Z", arg, re.IGNORECASE):
        m = 6
    
    if m=='' and allow_index:
        match = re.search("\A\s*\(\s*IX\s*(.*)\s*\)\s*\Z", arg, re.IGNORECASE)
        if match:
            m = 6
            prefix = [0xdd]
            offset = match.group(1)
            if offset == '' or p!=2:
                postfix = [0]
            else:
                if not allow_offset:
                    fatal ("Index register offset not allowed in this instruction")
                postfix = [parse_expression(offset, byte=1)]
    
    if m=='' and allow_index:
        match = re.search("\A\s*\(\s*IY\s*(.*)\s*\)\s*\Z", arg, re.IGNORECASE)
        if match:
            m = 6
            prefix = [0xfd]
            offset = match.group(1)
            if offset == '' or p!=2:
                postfix = [0]
            else:
                if not allow_offset:
                    fatal ("Index register offset not allowed in this instruction")
                postfix = [parse_expression(offset, byte=1)]
    
    return prefix,m,postfix

def condition(arg):
# decode condition [nz, z, nc, c, po, pe, p, m]
    condition_mapping = {'NZ':0, 'Z':1, 'NC':2, 'C':3, 'PO':4, 'PE':5, 'P':6, 'M':7 }
    return condition_mapping.get(arg.upper(),'')


def dump(bytes):
    def initpage(page):
        memory[page] = array.array('B')
        
        memory[page].append(0)
        while len(memory[page]) < 16384:
            memory[page].extend(memory[page])
    
    global dumppage, dumporigin
    
    if (p==2):
        
        if memory[dumppage]=='':
            initpage(dumppage)
        
        for b in bytes:
           # if b<0 or b>255:
           #     warning("Dump byte out of range")
            memory[dumppage][dumporigin] = b
            
            dumporigin += 1
            if dumporigin == 16384:
                dumporigin = 0
                dumppage += 1
                
                if memory[dumppage]=='':
                    initpage(dumppage)

def check_args(args,expected):
    if args=='':
        received = 0
    else:
        received = len(args.split(','))
    if expected!=received:
        fatal("Opcode wrong number of arguments, expected "+str(expected)+" received "+str(args))

def op_EQU(p,opargs):
    global symboltable
    check_args(opargs,1)
    if (symbol):
        if p==1:
            symboltable[symbol] = parse_expression(opargs, signed=1, silenterror=1)
        else:
            expr_result = parse_expression(opargs, signed=1)
            
            if symboltable[symbol] == '':
                symboltable[symbol] = expr_result
            elif symboltable[symbol] != parse_expression(opargs, signed=1):
                fatal("Symbol "+symbol+": expected "+str(symboltable[symbol])+" but calculated "+str(parse_expression(opargs, signed=1))+", has this symbol been used twice?")
    else:
        warning("EQU without symbol name")
    return 0

def op_ORG(p,opargs):
    global origin
    check_args(opargs,1)
    origin = parse_expression(opargs, word=1)
    return 0

def op_DUMP(p,opargs):
    global dumppage, dumporigin, firstpage, firstpageoffset
    if ',' in opargs:
        page,offset = opargs.split(',',1)
        offset = parse_expression(offset, word=1)
        dumppage = parse_expression(page) + (offset / 16384)
        dumporigin = offset % 16384
    else:
        offset = parse_expression(opargs)
        if (offset<16384):
            error ("DUMP value out of range")
        dumppage = (offset / 16384) - 1
        dumporigin = offset % 16384
    
    if ((dumppage*16384 + dumporigin) < (firstpage*16384 + firstpageoffset)):
        firstpage = dumppage
        firstpageoffset = dumporigin
    
    return 0

def op_AUTOEXEC(p,opargs):
    global autoexecpage, autoexecorigin
    check_args(opargs,0)
    if (p==2):
        if (autoexecpage>0 or autoexecorigin>0):
            fatal("AUTOEXEC may only be used once.");
        autoexecpage = dumppage + 1; # basic type page numbering
        autoexecorigin = dumporigin;

    
    return 0

def op_DS(p,opargs):
    return op_DEFS(p,opargs)
def op_DEFS(p,opargs):
    global dumppage, dumporigin
    check_args(opargs,1)
    s = parse_expression(opargs)
    if s<0:
        warning("Allocated space < 0 bytes")
    dumporigin += s
    dumppage += dumporigin / 16384
    dumporigin %= 16384
    return s

def op_DB(p,opargs):
    return op_DEFB(p,opargs)
def op_DEFB(p,opargs):
    s = opargs.split(',')
    if (p==2):
        for b in s:
            byte=(parse_expression(b, byte=1, silenterror=1))
            if byte=='':
                fatal("Didn't understand DB or character constant "+b)
            else:
                dump([byte])
    return len(s)

def op_DW(p,opargs):
    return op_DEFW(p,opargs)
def op_DEFW(p,opargs):
    s = opargs.split(',')
    if (p==2):
        for b in s:
            b=(parse_expression(b, word=1))
            dump([b%256, b/256])
    return 2*len(s)

def op_DM(p,opargs):
    return op_DEFM(p,opargs)
def op_DEFM(p,opargs):
    match = re.search('\A\s*\"(.*)\"\s*\Z', opargs)
    message = list(match.group(1))
    if p==2:
        for i in message:
            dump ([ord(i)])
    return len(message)

def op_MDAT(p,opargs):
    global dumppage, dumporigin
    match = re.search('\A\s*\"(.*)\"\s*\Z', opargs)
    filename = global_path + match.group(1)
    
    try:
        mdatfile = open(filename,'rb')
    except:
        fatal("Unable to open file for reading: "+filename)
    
    mdatfile.seek(0,2)
    filelength = mdatfile.tell()
    if p==1:
        dumporigin += filelength
        dumppage += dumporigin / 16384
        dumporigin %= 16384
    elif p==2:
        mdatfile.seek(0)
        mdatafilearray = array.array('B')
        mdatafilearray.fromfile(mdatfile, filelength)
        dump(mdatafilearray)
    
    mdatfile.close()
    return filelength

def op_INCLUDE(p,opargs):
    global global_path
    
    savedorigin = origin
    
    match = re.search('\A\s*\"(.*)\"\s*\Z', opargs)
    filename = match.group(1)
    
    old_path = global_path
    assembler_pass(p, filename)
    global_path = old_path
    
    return 0
    # global origin has already been updated


def op_FOR(p,opargs):
    args = opargs.split(',',1)
    limit = parse_expression(args[0])
    bytes = 0
    for iterate in range(limit):
        symboltable['FOR'] = iterate
        if CASE:
            symboltable['for'] = iterate
        bytes += assemble_instruction(p,args[1].strip())
    
    return bytes

def op_noargs_type(p,opargs,instr):
    check_args(opargs,0)
    if (p==2):
        dump(instr)
    return len(instr)

def op_NOP(p,opargs):
    return op_noargs_type(p,opargs,[0x00])
def op_RLCA(p,opargs):
    return op_noargs_type(p,opargs,[0x07])
def op_RRCA(p,opargs):
    return op_noargs_type(p,opargs,[0x0F])
def op_RLA(p,opargs):
    return op_noargs_type(p,opargs,[0x17])
def op_RRA(p,opargs):
    return op_noargs_type(p,opargs,[0x1F])
def op_DAA(p,opargs):
    return op_noargs_type(p,opargs,[0x27])
def op_CPL(p,opargs):
    return op_noargs_type(p,opargs,[0x2F])
def op_SCF(p,opargs):
    return op_noargs_type(p,opargs,[0x37])
def op_CCF(p,opargs):
    return op_noargs_type(p,opargs,[0x3F])
def op_HALT(p,opargs):
    return op_noargs_type(p,opargs,[0x76])
def op_DI(p,opargs):
    return op_noargs_type(p,opargs,[0xf3])
def op_EI(p,opargs):
    return op_noargs_type(p,opargs,[0xfb])
def op_EXX(p,opargs):
    return op_noargs_type(p,opargs,[0xd9])
def op_NEG(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0x44])
def op_RETN(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0x45])
def op_RETI(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0x4d])
def op_RRD(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0x67])
def op_RLD(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0x6F])
def op_LDI(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xa0])
def op_CPI(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xa1])
def op_INI(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xa2])
def op_OUTI(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xa3])
def op_LDD(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xa8])
def op_CPD(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xa9])
def op_IND(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xaa])
def op_OUTD(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xab])
def op_LDIR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xb0])
def op_CPIR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xb1])
def op_INIR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xb2])
def op_OTIR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xb3])
def op_LDDR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xb8])
def op_CPDR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xb9])
def op_INDR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xba])
def op_OTDR(p,opargs):
    return op_noargs_type(p,opargs,[0xed,0xbb])

def op_cbshifts_type(p,opargs,offset,step_per_register=1):
    args = opargs.split(',',1)
    if len(args) == 2:
        # composite instruction of the form RLC
        error("Composite instructions not yet supportted")
    else:
        check_args(opargs,1)
        pre,r,post = single(opargs,allow_half=0)
        instr = pre
        instr.extend([0xcb])
        instr.extend(post)
        if r=='':
            fatal ("Invalid argument")
        else:
            instr.append(offset + step_per_register*r)
        if (p==2):
            dump(instr)
        return len(instr)

def op_RLC(p,opargs):
    return op_cbshifts_type(p,opargs,0x00)
def op_RRC(p,opargs):
    return op_cbshifts_type(p,opargs,0x08)
def op_RL(p,opargs):
    return op_cbshifts_type(p,opargs,0x10)
def op_RR(p,opargs):
    return op_cbshifts_type(p,opargs,0x18)
def op_SLA(p,opargs):
    return op_cbshifts_type(p,opargs,0x20)
def op_SRA(p,opargs):
    return op_cbshifts_type(p,opargs,0x28)
def op_SLL(p,opargs):
    if (p==1):
        warning("SLL doesn't do what you probably expect on z80b! Use SL1 if you know what you're doing.")
    return op_cbshifts_type(p,opargs,0x30)
def op_SL1(p,opargs):
    return op_cbshifts_type(p,opargs,0x30)
def op_SRL(p,opargs):
    return op_cbshifts_type(p,opargs,0x38)



def op_register_arg_type(p,opargs,offset,ninstr,step_per_register=1):
    check_args(opargs,1)
    pre,r,post = single(opargs,allow_half=1)
    instr = pre
    if r=='':
        instr.extend(ninstr)
        if (p==2):
            n = parse_expression(opargs, byte=1)
        else:
            n = 0
        instr.append(n)
    else:
        instr.append(offset + step_per_register*r)
    instr.extend(post)
    if (p==2):
        dump(instr)
    return len(instr)

def op_SUB(p,opargs):
    return op_register_arg_type(p,opargs, 0x90, [0xd6])
def op_AND(p,opargs):
    return op_register_arg_type(p,opargs, 0xa0, [0xe6])
def op_XOR(p,opargs):
    return op_register_arg_type(p,opargs, 0xa8, [0xee])
def op_OR(p,opargs):
    return op_register_arg_type(p,opargs, 0xb0, [0xf6])
def op_CP(p,opargs):
    return op_register_arg_type(p,opargs, 0xb8, [0xfe])

def op_registerorpair_arg_type(p,opargs,rinstr,rrinstr,step_per_register=8,step_per_pair=16):
    check_args(opargs,1)
    pre,r,post = single(opargs)
    
    if r=='':
        pre,rr = double(opargs)
        if rr=='':
            fatal ("Invalid argument")
        
        instr = pre
        instr.append(rrinstr + step_per_pair*rr)
    else:
        instr = pre
        instr.append(rinstr + step_per_register*r)
        instr.extend(post)
    if (p==2):
        dump(instr)
    return len(instr)

def op_INC(p,opargs):
# Oh dear - COMET also used "INC" for INClude source file
    if '"' in opargs:
        return op_INCLUDE(p,opargs)
    
    return op_registerorpair_arg_type(p,opargs, 0x04, 0x03)
def op_DEC(p,opargs):
    return op_registerorpair_arg_type(p,opargs, 0x05, 0x0b)

def op_add_type(p,opargs,rinstr,ninstr,rrinstr,step_per_register=1,step_per_pair=16):
    args = opargs.split(',',1)
    r=''
    
    if len(args) == 2:
        pre,r,post = single(args[0])
    
    if (len(args) == 1) or r==7:
        pre,r,post = single(args[-1])
        instr = pre
        if r=='':
            instr.extend(ninstr)
            if (p==2):
                n = parse_expression(args[-1], byte=1)
            else:
                n = 0
            instr.append(n)
        else:
            instr.extend(rinstr)
            instr[-1] += step_per_register*r
        
        instr.extend(post)
    else:
        pre,rr1 = double(args[0])
        dummy,rr2 = double(args[1])
        
        if (rr1 == rr2) and (pre != dummy):
            fatal ("Can't mix index registers and HL")
        if (len(rrinstr) > 1) and pre:
            fatal ("Can't use index registers in this instruction")
        
        if (len(args) != 2) or (rr1 != 2):
            fatal("Invalid argument")
        
        instr = pre
        instr.extend(rrinstr)
        instr[-1] += step_per_pair*rr2
    
    if (p==2):
        dump(instr)
    return len(instr)

def op_ADD(p,opargs):
    return op_add_type(p,opargs,[0x80], [0xc6],[0x09])
def op_ADC(p,opargs):
    return op_add_type(p,opargs,[0x88], [0xce],[0xed,0x4a])
def op_SBC(p,opargs):
    return op_add_type(p,opargs,[0x98], [0xde],[0xed,0x42])

def op_bit_type(p,opargs,offset):
    check_args(opargs,2)
    arg1,arg2 = opargs.split(',',1)
    b = parse_expression(arg1)
    if b>7 or b<0:
        fatal ("argument out of range")
    pre,r,post = single(arg2,allow_half=0)
    instr = pre
    instr.append(0xcb)
    instr.extend(post)
    instr.append(offset + r + 8*b)
    if (p==2):
        dump(instr)
    return len(instr)

def op_BIT(p,opargs):
    return op_bit_type(p,opargs, 0x40)
def op_RES(p,opargs):
    return op_bit_type(p,opargs, 0x80)
def op_SET(p,opargs):
    return op_bit_type(p,opargs, 0xc0)

def op_pushpop_type(p,opargs,offset):
    
    check_args(opargs,1)
    prefix, rr = double(opargs, allow_af_instead_of_sp=1)
    instr = prefix
    if rr=='':
        fatal ("Invalid argument")
    else:
        instr.append(offset + 16 * rr)
    if (p==2):
        dump(instr)
    return len(instr)

def op_POP(p,opargs):
    return op_pushpop_type(p,opargs, 0xc1)
def op_PUSH(p,opargs):
    return op_pushpop_type(p,opargs, 0xc5)

def op_jumpcall_type(p,opargs,offset, condoffset):
    args = opargs.split(',',1)
    if len(args) == 1:
        instr = [offset]
    else:
        cond = condition(args[0])
        if cond == '':
            fatal ("Expected condition, received "+opargs)
        instr = [condoffset + 8*cond]
    
    if (p==2):
        nn = parse_expression(args[-1],word=1)
        instr.extend([nn%256, nn/256])
        dump(instr)
    
    return 3

def op_JP(p,opargs):
    if (len(opargs.split(',',1)) == 1):
        prefix, r, postfix = single(opargs, allow_offset=0,allow_half=0)
        if r==6:
            instr = prefix
            instr.append(0xe9)
            if (p==2):
                dump(instr)
            return len(instr)
    return op_jumpcall_type(p,opargs, 0xc3, 0xc2)

def op_CALL(p,opargs):
    return op_jumpcall_type(p,opargs, 0xcd, 0xc4)

def op_DJNZ(p,opargs):
    check_args(opargs,1)
    if (p==2):
        target = parse_expression(opargs,word=1)
        displacement = target - (origin + 2)
        if displacement > 127 or displacement < -128:
            fatal ("Displacement from "+str(origin)+" to "+str(target)+" is out of range")
        dump([0x10,(displacement+256)%256])
    
    return 2

def op_JR(p,opargs):
    args = opargs.split(',',1)
    if len(args) == 1:
        instr = 0x18
    else:
        cond = condition(args[0])
        if cond == '':
            fatal ("Expected condition, received "+opargs)
        instr = 0x20 + 8*cond
    if (p==2):
        target = parse_expression(args[-1],word=1)
        displacement = target - (origin + 2)
        if displacement > 127 or displacement < -128:
            fatal ("Displacement from "+str(origin)+" to "+str(target)+" is out of range")
        dump([instr,(displacement+256)%256])
    
    return 2

def op_RET(p,opargs):
    if opargs=='':
        if (p==2):
            dump([0xc9])
    else:
        check_args(opargs,1)
        cond = condition(opargs)
        if cond == '':
            fatal ("Expected condition, received "+opargs)
        if (p==2):
            dump([0xc0 + 8*cond])
    return 1

def op_IM(p,opargs):
    check_args(opargs,1)
    if (p==2):
        mode = parse_expression(opargs)
        if (mode>2) or (mode<0):
            fatal ("argument out of range")
        if mode > 0:
            mode += 1
        
        dump([0xed, 0x46 + 8*mode])
    return 2

def op_RST(p,opargs):
    check_args(opargs,1)
    if (p==2):
        vector = parse_expression(opargs)
        if (vector>0x38) or (vector<0) or ((vector%8) != 0):
            fatal ("argument out of range or doesn't divide by 8")
        
        dump([0xc7 + vector])
    return 1

def op_EX(p,opargs):
    check_args(opargs,2)
    args = opargs.split(',',1)
    
    pre1,rr1 = double(args[0],allow_af_instead_of_sp=1, allow_index=0)
    pre2,rr2 = double(args[1],allow_af_instead_of_sp=1, allow_af_alt=1, allow_index=0)
    
    if ( rr1==1 and rr2==2 ) or ( rr1==2 and rr2==1):
        # EX DE,HL
        # or EX HL,DE (can't bring myself to disallow this alternative syntax)
        instr = pre1
        instr.extend(pre2)
        instr.append(0xeb)
    elif (rr1==3 and rr2==4):
        instr=[0x08]
    elif rr2==2 and re.search("\A\s*\(\s*SP\s*\)\s*\Z", args[0], re.IGNORECASE):
        instr = pre2
        instr.append(0xe3)
    else:
        fatal("Can't exchange "+args[0]+" with "+args[1])
    
    if (p==2):
        dump(instr)
    
    return len(instr)

def op_IN(p,opargs):
    check_args(opargs,2)
    args = opargs.split(',',1)
    if (p==2):
        pre,r,post = single(args[0],allow_index=0,allow_half=0)
        if r!='' and r!=6 and re.search("\A\s*\(\s*C\s*\)\s*\Z", args[1], re.IGNORECASE):
            dump([0xed, 0x40+8*r])
        elif r==7:
            match = re.search("\A\s*\(\s*(.*)\s*\)\s*\Z", args[1])
            if match==None:
                fatal("No expression in "+args[1])
            
            n = parse_expression(match.group(1))
            dump([0xdb, n])
        else:
            fatal("Invalid argument")
    return 2

def op_OUT(p,opargs):
    check_args(opargs,2)
    args = opargs.split(',',1)
    if (p==2):
        pre,r,post = single(args[1],allow_index=0,allow_half=0)
        if r!='' and r!=6 and re.search("\A\s*\(\s*C\s*\)\s*\Z", args[0], re.IGNORECASE):
            dump([0xed, 0x41+8*r])
        elif r==7:
            match = re.search("\A\s*\(\s*(.*)\s*\)\s*\Z", args[0])
            n = parse_expression(match.group(1))
            dump([0xd3, n])
        else:
            fatal("Invalid argument")
    return 2

def op_LD(p,opargs):
    check_args(opargs,2)
    arg1,arg2 = opargs.split(',',1)
    
    prefix, rr1 = double(arg1)
    if rr1 != '':
        prefix2, rr2 = double(arg2)
        if rr1==3 and rr2==2:
            instr = prefix
            instr.append(0xf9)
            dump(instr)
            return len(instr)
        
        match = re.search("\A\s*\(\s*(.*)\s*\)\s*\Z", arg2)
        if match:
            # ld rr, (nn)
            if p==2:
                nn = parse_expression(match.group(1),word=1)
            else:
                nn = 0
            instr = prefix
            if rr1==2:
                instr.extend([0x2a, nn%256, nn/256])
            else:
                instr.extend([0xed, 0x4b + 16*rr1, nn%256, nn/256])
            dump(instr)
            return len (instr)
        else:
            #ld rr, nn
            if p==2:
                nn = parse_expression(arg2,word=1)
            else:
                nn = 0
            instr = prefix
            instr.extend([0x01 + 16*rr1, nn%256, nn/256])
            dump(instr)
            return len (instr)
    
    prefix, rr2 = double(arg2)
    if rr2 != '':
        match = re.search("\A\s*\(\s*(.*)\s*\)\s*\Z", arg1)
        if match:
            # ld (nn), rr
            if p==2:
                nn = parse_expression(match.group(1))
            else:
                nn = 0
            instr = prefix
            if rr2==2:
                instr.extend([0x22, nn%256, nn/256])
            else:
                instr.extend([0xed, 0x43 + 16*rr2, nn%256, nn/256])
            dump(instr)
            return len (instr)
    
    prefix1,r1,postfix1 = single(arg1, allow_i=1, allow_r=1)
    prefix2,r2,postfix2 = single(arg2, allow_i=1, allow_r=1)
    if r1 != '' :
        if r2 != '':
            if (r1 > 7) or (r2 > 7):
                if r1==7:
                    if r2==8:
                        dump([0xed,0x57])
                        return 2
                    elif r2==9:
                        dump([0xed,0x5f])
                        return 2
                if r2==7:
                    if r1==8:
                        dump([0xed,0x47])
                        return 2
                    elif r1==9:
                        dump([0xed,0x4f])
                        return 2
                fatal("Invalid argument")
            
            if r1==6 and r2==6:
                fatal("Ha - nice try. That's a HALT.")
            
            if (r1==4 or r1==5) and (r2==4 or r2==5) and prefix1 != prefix2:
                fatal("Illegal combination of operands")
            
            instr = prefix1
            if len(prefix1) == 0:
                instr.extend(prefix2)
            instr.append(0x40 + 8*r1 + r2)
            instr.extend(postfix1)
            instr.extend(postfix2)
            dump(instr)
            return len(instr)
        
        else:
            if r1==7 and re.search("\A\s*\(\s*BC\s*\)\s*\Z", arg2, re.IGNORECASE):
                dump([0x0a])
                return 1
            if r1==7 and re.search("\A\s*\(\s*DE\s*\)\s*\Z", arg2, re.IGNORECASE):
                dump([0x1a])
                return 1
            match = re.search("\A\s*\(\s*(.*)\s*\)\s*\Z", arg2)
            if match:
                if p==2:
                    nn = parse_expression(match.group(1), word=1)
                    dump([0x3a, nn%256, nn/256])
                return 3
            
            instr = prefix1
            instr.append(0x06 + 8*r1)
            instr.extend(postfix1)
            if (p==2):
                n = parse_expression(arg2, byte=1)
            else:
                n = 0
            instr.append(n)
            dump(instr)
            return len(instr)
    
    elif r2==7:
        # ld (bc/de/nn),a
        if re.search("\A\s*\(\s*BC\s*\)\s*\Z", arg1, re.IGNORECASE):
            dump([0x02])
            return 1
        if re.search("\A\s*\(\s*DE\s*\)\s*\Z", arg1, re.IGNORECASE):
            dump([0x12])
            return 1
        match = re.search("\A\s*\(\s*(.*)\s*\)\s*\Z", arg1)
        if match:
            if p==2:
                nn = parse_expression(match.group(1), word=1)
                dump([0x32, nn%256, nn/256])
            return 3
    fatal("LD args not understood - "+arg1+", "+arg2)
    
    return 1

def assemble_instruction(p, line):
    opcodeargs = line.split(None,1)
# or spilt at first open bracket? Hurrah, let's reimplement a built-in function
    if len(opcodeargs)>1:
        args = opcodeargs[1].strip()
    else:
        args=''
    
    functioncall = 'op_'+opcodeargs[0].upper()+'(p,args)'
    if PYTHONERRORS:
        return eval(functioncall)
    else:
        try:
            return eval(functioncall)
        except:
            fatal("OpCode not recognised")

def assembler_pass(p, inputfile):
    global memory, symboltable, origin, dumppage, dumporigin, symbol
    global global_currentfile, global_currentline
# file references are local, so assembler_pass can be called recursively (for op_INC)
# but copied to a global identifier for warning printouts
    global global_path
    
    global_currentfile="command line"
    global_currentline="0"
    
    # just read the whole file into memory, it's not going to be huge (probably)
    # I'd prefer not to, but assembler_pass can be called recursively
    # (by op_INCLUDE for example) and fileinput does not support two files simultaneously
    
    this_currentfilename = global_path + inputfile
    
    currentfile = fileinput.input([this_currentfilename])
    if "/" in this_currentfilename:
        global_path = this_currentfilename[:this_currentfilename.rfind('/')+1]
    
    wholefile=[]
    try:
        for currentline in currentfile:
            wholefile.append(currentline)
    except:
        fatal("Couldn't open file "+this_currentfilename+" for reading")
    
    currentfile.close()
    
    consider_linenumber=0
    
    for currentline in wholefile:
        consider_linenumber+=1
        global_currentline = currentline
        global_currentfile = this_currentfilename+":"+repr(consider_linenumber)
            # write these every instruction because an INCLUDE may have overwritten them
        
        symbol = ''
        opcode = ''
        inquotes = 0
        
        for i in currentline:
            if (i==';' or i=='#') and not inquotes:
                break
            if i==':' and not inquotes:
                symbol = opcode
                opcode=''
                i = ''
            
            if i == '"':
                inquotes = not inquotes
                if lasti == '"':
                # comet form of " literal
                    i=''
            
            if inquotes or CASE:
                opcode += i
            else:
                opcode += i.upper()
            
            lasti = i
        
        symbol = symbol.strip()
        opcode = opcode.strip()
        
        
        if ' ' in symbol:
            fatal("Whitespace not allowed in symbol name")
        
        if (symbol and (opcode[0:3].upper() !="EQU")):
            if p==1:
                symboltable[symbol] = origin
            elif symboltable[symbol] != origin:
                fatal("Symbol "+symbol+": expected "+str(symboltable[symbol])+" but calculated "+str(origin)+", has this symbol been used twice?")
        
        if (opcode):
            bytes = assemble_instruction(p,opcode)
            origin = (origin + bytes) % 65536

    


###########################################################################

try:
    option_args, file_args = getopt.getopt(sys.argv[1:], 'ho:s:eD:', ['version','help','nozip','case'])
except getopt.GetoptError:
    printusage()
    sys.exit(2)

inputfile = ''
outputfile = ''

PYTHONERRORS = False
ZIP = True
CASE = False

listsymbols=[]
predefsymbols=[]

for option,value in option_args:
    if option in ('--version'):
        printusage()
        print("")
        printlicense()
        sys.exit(0)
    if option in ('--help','-h'):
        printusage()
        sys.exit(0)
    
    if option in ('-o'):
        outputfile=value
    
    if option in ('-s'):
        listsymbols.append(value)
    
    if option in ('-e'):
        PYTHONERRORS = True # let python do its own error handling
    
    if option in ('--nozip'):
	    ZIP = False # save the disk image without compression
    
    if option in ('--case'):
        CASE = True

    if option in ('-D'):
        predefsymbols.append(value)

if len(file_args) == 0:
    print "No input file specified"
    printusage()
    sys.exit(2)

if len(file_args) > 1:
    print "Multiple input files specified"
    printusage()
    sys.exit(2)

inputfile = file_args[0]

if (outputfile == ''):
    outputfile = inputfile.split('/')[-1].split('.')[0] + ".dsk";




if inputfile == outputfile:
    print "Output file and input file are the same!"
    printusage()
    sys.exit(2)

symboltable = {}
memory = []

for value in predefsymbols:
    sym=value.split('=',1)
    if len(sym)==1:
        sym.append("1")
    if not CASE:
        sym[0]=sym[0].upper()
    if PYTHONERRORS:
        val = int(sym[1])
    else:
        try:
            val = int(sym[1])
        except:
            print("Error: Invalid value for symbol predefined on command line, "+value)
            sys.exit(1)
    
    symboltable[sym[0]]=int(sym[1])


firstpage=32
firstpageoffset=16384

# always 32 memory pages, each a 16k array allocate-on-write
for initmemorypage in range(32):
    memory.append('')

for p in 1,2:
    print "pass ",p,"..."
    
    global_path=''
    
    origin = 32768
    dumppage = 1
    dumporigin = 0
    autoexecpage = 0
    autoexecorigin = 0
    
    assembler_pass(p, inputfile)

printsymbols = {}
for symreg in listsymbols:
    # add to printsymbols any pair from symboltable whose key matches symreg
    for sym in symboltable:
        if re.search(symreg, sym, re.IGNORECASE):
            printsymbols[sym] = symboltable[sym]

if printsymbols != {}:
    print printsymbols

make_disk_image(memory, outputfile)

print "Finished"
