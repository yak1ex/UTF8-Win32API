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
