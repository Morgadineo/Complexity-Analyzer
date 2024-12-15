#include <stdio.h>

int main(void) {
    int n = 5;
    
    for (int i = 0; i <= 10; i++) {
        printf("%d x %d = %d\n", n, i, n * i);
    }
    
    return 0;
}

