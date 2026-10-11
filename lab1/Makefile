CC = gcc
CFLAGS = -Og -Wall

all: main.o sum.o prog

main.o: main.c
	$(CC) $(CFLAGS) -c main.c -o main.o

sum.o: sum.c
	$(CC) $(CFLAGS) -c sum.c -o sum.o

prog: main.o sum.o
	$(CC) $(CFLAGS) -o prog main.o sum.o

clean:
	rm -f *.o prog

.PHONY: all clean
