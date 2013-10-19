CC=i686-w64-mingw32-gcc
CXX=i686-w64-mingw32-g++
CFLAGS=-Wall -pedantic -DWINVER=0x0500
CXXFLAGS=-Wall -pedantic -Ic:/cygwin/usr/local/include -DWINVER=0x0500

OBJS=$(patsubst %u.cpp,%u.o,$(wildcard *u.cpp))

test: libwin32u.a test.o
	$(CXX) -o $@ $^ -L. -lwin32u

testrun: testrunner
	./testrunner --log-level=warning

testrunner: $(patsubst test_%.c,test_%.o,$(wildcard test_*.c)) $(patsubst test%.cpp,test%.o,$(wildcard test*.cpp)) libwin32u.a
	$(CXX) -o $@ $^

generate:
	-rm -f *u.txt *u.cpp *u.h
	-python apigenerate.py /usr/include/w32api/windows.h
	-python crtgenerate.py /usr/i686-w64-mingw32/sys-root/mingw/include msvcrt.h

clean:
	-rm -rf *.o *.a *.exe *u.txt *u.cpp *u.h *.pyc

libwin32u.a: generate win32u_helper.o $(OBJS)
	$(AR) ru $@ win32u_helper.o $(OBJS)

%.h: %.txt
	perl header.pl $< $@

win32u_helper.o: win32u_helper.cpp win32u_helper.hpp
#winbaseu.o: winbaseu.cpp winbaseu.h win32u.hpp
#winuseru.o: winuseru.cpp winuseru.h win32u.hpp
#shellapiu.o: shellapiu.cpp shellapiu.h win32u.hpp
#psapiu.o: psapiu.cpp psapiu.h win32u.hpp
#winnlsu.o: winnlsu.cpp winnlsu.h win32u.hpp
