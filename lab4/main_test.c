#include <stdio.h>

extern int g_counter1;
extern int g_counter2;
int math_add(int a, int b);
int math_sub(int a, int b);

int main() {
    int res1 = math_add(10, 20);
    int res2 = math_sub(50, 15);
    printf("math_add(10, 20) = %d (g_counter1 = %d)\n", res1, g_counter1);
    printf("math_sub(50, 15) = %d (g_counter2 = %d)\n", res2, g_counter2);
    return 0;
}
