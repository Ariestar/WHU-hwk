CC = gcc
CFLAGS = -Og -Wall

all: static_lib prog2c dynamic_lib prog2r

static_lib: addvec.c multvec.c
	$(CC) $(CFLAGS) -c addvec.c multvec.c
	ar rcs libvector.a addvec.o multvec.o

prog2c: main2.c static_lib
	$(CC) $(CFLAGS) -c main2.c
	$(CC) $(CFLAGS) -static -o prog2c main2.o ./libvector.a

dynamic_lib: addvec.c multvec.c
	$(CC) $(CFLAGS) -shared -fpic -o libvector.so addvec.c multvec.c

prog2r: dll.c dynamic_lib
	$(CC) $(CFLAGS) -rdynamic -o prog2r dll.c -ldl

clean:
	rm -f *.o *.a *.so prog2c prog2r

.PHONY: all static_lib dynamic_lib clean
