CFLAGS=-Wall -pedantic -DWINVER=0x0500
CXXFLAGS=-Wall -pedantic -I/usr/include/boost -DWINVER=0x0500

test: libwin32u.a test.o
	$(CXX) -o $@ $^ -L. -lwin32u

testrun: testrunner
	./testrunner --log-level=warning

testrunner: $(patsubst test_%.c,test_%.o,$(wildcard test_*.c)) $(patsubst test%.cpp,test%.o,$(wildcard test*.cpp)) libwin32u.a
	$(CXX) -o $@ $^

clean:
	-rm -rf *.o *.a *.exe *.h.txt *.h.cpp

libwin32u.a: win32u.o # winbaseu.o winuseru.o shellapiu.o psapiu.o winnlsu.o
	$(AR) ru $@ $?

%.h: %.txt
	perl header.pl $< $@

win32u.o: win32u.cpp win32u.hpp
#winbaseu.o: winbaseu.cpp winbaseu.h win32u.hpp
#winuseru.o: winuseru.cpp winuseru.h win32u.hpp
#shellapiu.o: shellapiu.cpp shellapiu.h win32u.hpp
#psapiu.o: psapiu.cpp psapiu.h win32u.hpp
#winnlsu.o: winnlsu.cpp winnlsu.h win32u.hpp
