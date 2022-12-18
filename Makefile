all: test clean release

requireversion:
ifndef VERSION
	$(error No version to release, try "make VERSION=1.0")
endif

OUTDIR = pyz80-release
OUTFILE = pyz80-$(VERSION).tgz

FILES = $(OUTDIR) \
	$(OUTDIR)/pyz80 \
	$(OUTDIR)/COPYING \
	$(OUTDIR)/READ\ ME.rtf


release: requireversion $(FILES)
	tar zcf $(OUTFILE) $(OUTDIR) 



clean:
	rm -rf *-release *.tgz *.dsk *.dsk.gz



$(OUTDIR):
	mkdir $(OUTDIR)

$(OUTDIR)/pyz80: pyz80.py
	cp $< $@
	chmod +x $@

$(OUTDIR)/COPYING: COPYING
	cp $< $@

$(OUTDIR)/READ\ ME.rtf: READ\ ME.rtf
	cp "$<" "$@"


test: testing/test.z80s testing/include.z80s
	./pyz80.py -o test.dsk.gz -s . testing/test.z80s
	cp testing/golden.dsk.gz golden.dsk.gz
	gunzip -f test.dsk.gz golden.dsk.gz
	cat /dev/zero | dd conv=notrunc of=test.dsk bs=1 seek=245 count=5 # test.o file timestamp non-deterministic
	cmp test.dsk golden.dsk
	@echo --== TESTING COMPLETED OK ==--


