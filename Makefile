.PHONY: all
all: libwin32u.a

.PHONY: generate
generate:
	$(MAKE) -f Makefile.generate .generate

clean:
	-rm -rf *.o *.a *.exe *u.txt *u.cpp *u.h *.pyc .generate odstream/*.o

test: generate
testrun: generate
testrunner: generate

%.a: generate
	$(MAKE) -f Makefile.work $@

%:
	$(MAKE) -f Makefile.work $@

force: ;

repatch: perl-5.18.1-orig
	rm -rf perl-5.18.1
	cp -pR perl-5.18.1-orig perl-5.18.1
	chmod +w `grep +++ perl-5.18.1.patch | sed 's,+++ ,,;s,201.*,,'`
	patch -p0 < perl-5.18.1.patch

mkpatch:
	-env LANG=C diff -ur perl-5.18.1-orig perl-5.18.1 | grep -v '^Only in ' > perl-5.18.1.patch

initpatch: perl-5.18.1-orig
	@: nothing

perl-5.18.1-orig: perl-5.18.1.tar.gz
	rm -rf temp perl-5.18.1-orig
	mkdir temp
	tar xzf perl-5.18.1.tar.gz -C temp
	mv temp/perl-5.18.1 perl-5.18.1-orig
	rmdir temp

perl-5.18.1.tar.gz:
	wget http://search.cpan.org/CPAN/authors/id/R/RJ/RJBS/perl-5.18.1.tar.gz
