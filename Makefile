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

CUR = 5.18.2
VERS = 5.18.1 5.18.2

repatch: repatch_$(CUR)
	@: nothing

mkpatch: mkpatch_$(CUR)
	@: nothing

initpatch: initpatch_$(CUR)
	@: nothing

define TARGETS_template =
repatch_$(1): ./.extract$(1)
	rm -rf perl-$(1)
	cp -pR perl-$(1)-orig perl-$(1)
	chmod +w `grep +++ perl-$(1).patch | sed 's,+++ ,,;s,201.*,,'`
	patch -p0 < perl-$(1).patch

mkpatch_$(1):
	-env LANG=C diff -ur perl-$(1)-orig perl-$(1) | grep -v '^Only in ' > perl-$(1).patch

initpatch_$(1): ./.extract$(1)
	@: nothing

./.extract$(1): perl-$(1).tar.gz
	rm -rf temp perl-$(1)-orig
	mkdir temp
	tar xzf perl-$(1).tar.gz -C temp
	mv temp/perl-$(1) perl-$(1)-orig
	rmdir temp
	touch .extract$(1)

perl-$(1).tar.gz:
	wget http://search.cpan.org/CPAN/authors/id/R/RJ/RJBS/perl-$(1).tar.gz
endef

$(foreach ver,$(VERS),$(eval $(call TARGETS_template,$(ver))))
