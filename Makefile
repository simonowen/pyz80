all: test clean release

requireversion:
ifndef VERSION
	$(error No version to release, try "make VERSION=1.0")
endif

OUTDIR = pyz80-release
OUTFILE = pyz80-$(VERSION).tgz

FILES = $(OUTDIR) \
		$(OUTDIR)/pyz80 \
		$(OUTDIR)/COPYING


release: requireversion $(FILES)
	tar zcf $(OUTFILE) $(OUTDIR) 



clean:
	rm -rf *-release *.tgz *.dsk *.dsk.gz



$(OUTDIR):
	mkdir $(OUTDIR)

$(OUTDIR)/pyz80.py: pyz80.py
	cp $< $@
	chmod +x $@

$(OUTDIR)/pyz80: $(OUTDIR)/pyz80.py
	ln -s pyz80.py $@

$(OUTDIR)/COPYING: COPYING
	cp $< $@



test: testing/test.z80s testing/include.z80s
	./pyz80.py -o test.dsk.gz -s . testing/test.z80s
	cp testing/golden.dsk.gz golden.dsk.gz
	gunzip -f test.dsk.gz golden.dsk.gz
	cmp test.dsk golden.dsk
	@echo --== TESTING COMPLETED OK ==--


