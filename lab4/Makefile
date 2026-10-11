CC = gcc
CFLAGS = -Og -Wall

all: mylib test1.o test2.o

mylib: mylib.c
	$(CC) $(CFLAGS) -o mylib mylib.c

test1.o: test1.c
	$(CC) $(CFLAGS) -c test1.c -o test1.o

test2.o: test2.c
	$(CC) $(CFLAGS) -c test2.c -o test2.o

clean:
	rm -f mylib *.o *.a test_prog extracted_*.o

.PHONY: all clean
