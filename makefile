CC = clang
CFLAGS = -Wall -std=c99 -pedantic

all: libmol.so _molecule.so molecule.py main

mol.o: mol.c mol.h
		$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

libmol.so: mol.o
		$(CC) $(CFLAGS) mol.o -shared -o libmol.so

molecule_wrap.o: molecule_wrap.c
		$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I/usr/include/python3.7m -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
		$(CC) $(CFLAGS) -shared molecule_wrap.o -L. -L/user/lib/python3.7/config-3.7m-x86_64-linux-gnu -lpython3.7m -lmol -dynamiclib -o _molecule.so

main:
	python3 server.py 55001 /

clean:
		rm -f *.o *.so main