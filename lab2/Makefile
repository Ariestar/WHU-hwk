CC = gcc
CFLAGS = -Og -Wall

all: main.o sum.o prog prog_nopie

main.o: main.c
	$(CC) $(CFLAGS) -c main.c -o main.o

sum.o: sum.c
	$(CC) $(CFLAGS) -c sum.c -o sum.o

prog: main.o sum.o
	$(CC) $(CFLAGS) -o prog main.o sum.o

prog_nopie: main.c sum.c
	$(CC) $(CFLAGS) -no-pie -o prog_nopie main.c sum.c

clean:
	rm -f *.o prog prog_nopie

.PHONY: all clean
