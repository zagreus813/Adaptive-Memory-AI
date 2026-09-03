#include <stdio.h>
#include <stdlib.h>

#define SIZE 4096

int main(void)
{
    int *array = malloc(SIZE * sizeof(int));

    if (array == NULL) {
        return 1;
    }
    printf("ARRAY_BASE=%p\n", (void *)array);
    printf("ARRAY_END=%p\n", (void *)(array + SIZE));
    /* Sequential writes */
    for (int i = 0; i < SIZE; i++) {
        array[i] = i;
    }

    /* Sequential reads */
    long sum = 0;

    for (int i = 0; i < SIZE; i++) {
        sum += array[i];
    }

    /* Reuse a smaller working set */
    for (int r = 0; r < 100; r++) {
        for (int i = 0; i < 256; i++) {
            array[i] += 1;
        }
    }

    printf("sum = %ld\n", sum);

    free(array);

    return 0;
}
