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


/*
 * Default deterministic seed.
 *
 * Can be overridden from command line:
 *
 *     ./hot_cold 1111
 */
static uint32_t rng_state = 0x12345678u;


/*
 * xorshift32 PRNG
 *
 * Better than the previous LCG for this controlled
 * experiment because we do not want strong patterns
 * in the low-order bits.
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
 * Generate a random integer in:
 *
 *     [0, bound)
 *
 * Multiply-high avoids depending directly on
 * modulo of the low PRNG bits.
 */
static uint32_t random_bounded(
    uint32_t bound
)
{
    if (bound == 0) {
        return 0;
    }

    uint64_t value =
        (uint64_t)fast_rand()
        * (uint64_t)bound;

    return (uint32_t)(
        value >> 32
    );
}


int main(
    int argc,
    char **argv
)
{
    /*
     * Optional seed from command line.
     */
    if (argc >= 2) {

        unsigned long parsed_seed =
            strtoul(
                argv[1],
                NULL,
                0
            );


        /*
         * xorshift32 must not use zero state.
         */
        if (parsed_seed == 0) {
            parsed_seed = 1;
        }


        rng_state =
            (uint32_t)parsed_seed;
    }


    uint32_t initial_seed =
        rng_state;


    /*
     * Allocate exactly 256 pages and ensure that
     * the first byte is aligned to a 4 KB boundary.
     *
     * This gives us:
     *
     *     256 logical pages
     *     =
     *     256 OS pages
     */
    int *array = NULL;


    int rc = posix_memalign(
        (void **)&array,
        PAGE_SIZE,
        TOTAL_INTS * sizeof(int)
    );


    if (
        rc != 0
        || array == NULL
    ) {

        fprintf(
            stderr,
            "posix_memalign failed\n"
        );

        return 1;
    }


    /*
     * Metadata used by the trace-processing pipeline.
     */
    printf(
        "RNG_SEED=%u\n",
        initial_seed
    );


    printf(
        "ARRAY_BASE=%p\n",
        (void *)array
    );


    printf(
        "ARRAY_END=%p\n",
        (void *)(array + TOTAL_INTS)
    );


    /*
     * ------------------------------------------------
     * Initialization phase
     * ------------------------------------------------
     *
     * Touch every integer once.
     *
     * Expected accesses:
     *
     *     256 pages
     *     × 4096 bytes
     *     / 4 bytes per int
     *
     *     = 262,144 writes
     *
     * This phase is removed from the final
     * measurement trace.
     */
    for (
        uint32_t i = 0;
        i < TOTAL_INTS;
        i++
    ) {

        array[i] =
            (int)i;
    }


    long long checksum = 0;


    /*
     * ------------------------------------------------
     * Measurement phase
     * ------------------------------------------------
     *
     * 90% of accesses target 16 hot pages.
     *
     * 10% of accesses target the remaining
     * 240 cold pages.
     */
    for (
        uint32_t i = 0;
        i < ACCESSES;
        i++
    ) {

        /*
         * Value in:
         *
         *     [0, 100)
         */
        uint32_t probability =
            random_bounded(
                100
            );


        uint32_t page;


        /*
         * 90% Hot
         */
        if (
            probability < 90
        ) {

            page =
                random_bounded(
                    HOT_PAGES
                );

        }

        /*
         * 10% Cold
         */
        else {

            page =
                HOT_PAGES
                +
                random_bounded(
                    TOTAL_PAGES
                    - HOT_PAGES
                );
        }


        /*
         * Random integer offset inside
         * the selected 4 KB page.
         */
        uint32_t offset =
            random_bounded(
                INTS_PER_PAGE
            );


        uint32_t index =
            (
                page
                * INTS_PER_PAGE
            )
            + offset;


        /*
         * Main READ.
         *
         * Exactly 200,000 reads originate here.
         */
        checksum +=
            array[index];


        /*
         * Every 20 iterations perform an
         * additional modification:
         *
         *     READ + WRITE
         *
         * For 200,000 iterations:
         *
         *     10,000 additional reads
         *     10,000 writes
         */
        if (
            (i % 20) == 0
        ) {

            array[index] += 1;
        }
    }


    printf(
        "checksum=%lld\n",
        checksum
    );


    free(
        array
    );


    return 0;
}
