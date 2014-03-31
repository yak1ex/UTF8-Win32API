.PHONY: all
all: libwin32u.a

.PHONY: generate sgenerate
generate:
	$(MAKE) -f Makefile.generate .generate

sgenerate:
	$(MAKE) -f Makefile.generate .sgenerate

./.generated:
	$(MAKE) -f Makefile.generate .generate

clean:
	-rm -rf {gensrc,helper,odstream}/*.o *.a *.exe gensrc/*.{txt,cpp} include/*u.h *.pyc .generate .sgenerate .generated

buildclean:
	-rm -rf {gensrc,helper,odstream}/*.o *.a *.exe

test: ./.generated
testrun: ./.generated
testrunner: ./.generated

%.a: ./.generated
	$(MAKE) -f Makefile.work $@

%:
	$(MAKE) -f Makefile.work $@

force: ;

# Current: 5.18.2

repatch: ./.extract5182
	rm -rf perl-5.18.2
	cp -pR perl-5.18.2-orig perl-5.18.2
	chmod +w `grep +++ perl-5.18.2.patch | sed 's,+++ ,,;s,201.*,,'`
	patch -p0 < perl-5.18.2.patch

mkpatch:
	-env LANG=C diff -ur perl-5.18.2-orig perl-5.18.2 | grep -v '^Only in ' > perl-5.18.2.patch

initpatch: ./.extract5182
	@: nothing

./.extract5182: perl-5.18.2.tar.gz
	rm -rf temp perl-5.18.2-orig
	mkdir temp
	tar xzf perl-5.18.2.tar.gz -C temp
	mv temp/perl-5.18.2 perl-5.18.2-orig
	rmdir temp
	touch .extract5182

perl-5.18.2.tar.gz:
	wget http://search.cpan.org/CPAN/authors/id/R/RJ/RJBS/perl-5.18.2.tar.gz

# Previous: 5.18.1

repatch5181: ./.extract5181
	rm -rf perl-5.18.1
	cp -pR perl-5.18.1-orig perl-5.18.1
	chmod +w `grep +++ perl-5.18.1.patch | sed 's,+++ ,,;s,201.*,,'`
	patch -p0 < perl-5.18.1.patch

mkpatch5181:
	-env LANG=C diff -ur perl-5.18.1-orig perl-5.18.1 | grep -v '^Only in ' > perl-5.18.1.patch

initpatch5181: ./.extract5181
	@: nothing

./.extract5181: perl-5.18.1.tar.gz
	rm -rf temp perl-5.18.1-orig
	mkdir temp
	tar xzf perl-5.18.1.tar.gz -C temp
	mv temp/perl-5.18.1 perl-5.18.1-orig
	rmdir temp
	touch .extract5181

perl-5.18.1.tar.gz:
	wget http://search.cpan.org/CPAN/authors/id/R/RJ/RJBS/perl-5.18.1.tar.gz
