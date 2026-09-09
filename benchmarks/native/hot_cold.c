#define _POSIX_C_SOURCE 200112L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>


#define PAGE_SIZE 4096

#define TOTAL_PAGES 256
#define HOT_PAGES 16

#define INTS_PER_PAGE \
    (PAGE_SIZE / sizeof(int))

#define TOTAL_INTS \
    (TOTAL_PAGES * INTS_PER_PAGE)

#define ACCESSES 200000


static uint32_t rng_state = 0x12345678u;


/*
 * xorshift32
 *
 * Better suited than the previous LCG for this
 * controlled memory-workload experiment.
 */
static uint32_t fast_rand(void)
{
    uint32_t x = rng_state;

    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;

    rng_state = x;

    return x;
}


/*
 * Map a 32-bit random value into [0, bound).
 *
 * Using multiply-high avoids relying directly on
 * weak low-order bits with modulo operations.
 */
static uint32_t random_bounded(
    uint32_t bound
)
{
    uint64_t value =
        (uint64_t)fast_rand() * bound;

    return (uint32_t)(
        value >> 32
    );
}


int main(void)
{
    int *array = NULL;


    /*
     * Page-align the allocation.
     *
     * Now:
     *
     * 256 logical pages
     * =
     * 256 OS pages
     */
    int rc = posix_memalign(
        (void **)&array,
        PAGE_SIZE,
        TOTAL_INTS * sizeof(int)
    );


    if (rc != 0 || array == NULL) {

        fprintf(
            stderr,
            "posix_memalign failed\n"
        );

        return 1;
    }


    printf(
        "ARRAY_BASE=%p\n",
        (void *)array
    );

    printf(
        "ARRAY_END=%p\n",
        (void *)(array + TOTAL_INTS)
    );


    /*
     * Initialization phase.
     *
     * This phase is removed later from the
     * measurement trace.
     */
    for (
        int i = 0;
        i < TOTAL_INTS;
        i++
    ) {

        array[i] = i;
    }


    long long checksum = 0;


    for (
        int i = 0;
        i < ACCESSES;
        i++
    ) {

        uint32_t probability =
            random_bounded(100);


        uint32_t page;


        /*
         * 90% of iterations access
         * the hot working set.
         */
        if (probability < 90) {

            page = random_bounded(
                HOT_PAGES
            );

        } else {

            page =
                HOT_PAGES
                +
                random_bounded(
                    TOTAL_PAGES
                    - HOT_PAGES
                );
        }


        uint32_t offset =
            random_bounded(
                INTS_PER_PAGE
            );


        uint32_t index =
            page * INTS_PER_PAGE
            + offset;


        /*
         * Main read.
         */
        checksum += array[index];


        /*
         * Every 20 iterations perform
         * an additional modification.
         */
        if ((i % 20) == 0) {

            array[index] += 1;
        }
    }


    printf(
        "checksum=%lld\n",
        checksum
    );


    free(array);

    return 0;
}
