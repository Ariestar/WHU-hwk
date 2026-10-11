all:
	$(MAKE) -C lab1
	$(MAKE) -C lab2
	$(MAKE) -C lab3
	$(MAKE) -C lab4

clean:
	$(MAKE) -C lab1 clean
	$(MAKE) -C lab2 clean
	$(MAKE) -C lab3 clean
	$(MAKE) -C lab4 clean

test: all
	@echo "=== Testing Lab 1 ==="
	./lab1/prog || test $$? -eq 3
	@echo "=== Testing Lab 2 ==="
	./lab2/prog || test $$? -eq 3
	./lab2/calc.py
	@echo "=== Testing Lab 3 ==="
	cd lab3 && ./prog2c
	cd lab3 && ./prog2r
	@echo "=== Testing Lab 4 ==="
	cd lab4 && ./mylib -c libtest.a test1.o test2.o
	cd lab4 && ./mylib -t libtest.a
	cd lab4 && ./mylib -s libtest.a
	gcc -o lab4/test_prog lab4/main_test.c ./lab4/libtest.a
	./lab4/test_prog
	@echo "=== All Tests Passed! ==="

.PHONY: all clean test
