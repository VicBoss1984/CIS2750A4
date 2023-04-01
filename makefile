# HUGE THANKS to Niloy Gosh for assisting me with this makefile.
# I based this makefile on the makefiles the TAs demonstrated in the labs and fixed it with Niloy's help
UNAME := $(shell uname)
CC = clang
CFLAGS = -Wall -std=c99 -pedantic

INC := $(if $(findstring Darwin, $(UNAME)), /Library/Frameworks/Python.framework/Versions/3.11/include/python3.11, /usr/include/python3.7m)
LIB := $(if $(findstring Darwin, $(UNAME)), /Library/Frameworks/Python.framework/Versions/3.11/lib, /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu)
PYTHON_VERSION := $(if $(findstring Darwin, $(UNAME)), python3.11, python3.7m)

all: _molecule.so

libmol.so: mol.o
	$(CC) -shared mol.o -o libmol.so -lm

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c -fPIC mol.c -o mol.o

molecule_wrap.c: molecule.i mol.h
	swig -python molecule.i

molecule.py: molecule.i mol.h
	swig -python molecule.i

molecule_wrap.o: swig molecule_wrap.c
	$(CC) $(CFLAGS) -c -fPIC -I$(INC) molecule_wrap.c -o molecule_wrap.o

swig: molecule.i
	swig -python molecule.i

_molecule.so: libmol.so molecule_wrap.o
	$(CC) $(CFLAGS) -shared -L. -lmol -L$(LIB) -l$(PYTHON_VERSION) -dynamiclib -o _molecule.so molecule_wrap.o

clean:
	rm -f *.o *.so
