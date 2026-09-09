from collections import Counter

from traces.region import MemoryRegionLoader
from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter
from ai.labeler import NextUseLabeler


TRACE_FILE = (
    "datasets/raw/valgrind/hot_cold.log"
)

META_FILE = (
    "datasets/raw/valgrind/hot_cold.meta"
)


PAGE_SIZE = 4096

TOTAL_PAGES = 256
HOT_PAGES = 16

INT_SIZE = 4

# Number of array writes performed by
# the initialization loop.
INIT_ACCESSES = (
    TOTAL_PAGES
    * PAGE_SIZE
    // INT_SIZE
)


# --------------------------------------------------
# Load memory region
# --------------------------------------------------

region = MemoryRegionLoader.load(
    META_FILE
)

base_address = int(
    region["base"],
    16
)


# --------------------------------------------------
# Parse complete application array trace
# --------------------------------------------------

parser = ValgrindTraceParser(
    min_address=region["base"],
    max_address=region["end"]
)

address_trace = parser.parse(
    TRACE_FILE
)


print("========== RAW TRACE ==========")

print(
    "Total array accesses:",
    len(address_trace)
)

print(
    "Initialization accesses:",
    INIT_ACCESSES
)


# --------------------------------------------------
# Remove initialization phase
# --------------------------------------------------

measurement_trace = address_trace[
    INIT_ACCESSES:
]


print(
    "Measurement accesses:",
    len(measurement_trace)
)


# --------------------------------------------------
# Address -> page trace
# --------------------------------------------------

converter = AddressConverter(
    page_size=PAGE_SIZE
)

page_trace = converter.convert_trace(
    measurement_trace
)


unique_pages = {
    access["page_id"]
    for access in page_trace
}


print(
    "Unique measurement pages:",
    len(unique_pages)
)


# --------------------------------------------------
# Read / Write statistics
# --------------------------------------------------

reads = sum(
    access["operation"] == "READ"
    for access in page_trace
)

writes = sum(
    access["operation"] == "WRITE"
    for access in page_trace
)


print("\n========== OPERATIONS ==========")

print("Reads:", reads)
print("Writes:", writes)


# --------------------------------------------------
# Determine real OS pages containing the logical
# hot region.
#
# Because malloc is not page aligned, 16 logical
# pages may span 17 OS pages.
# --------------------------------------------------

hot_bytes = (
    HOT_PAGES
    * PAGE_SIZE
)

hot_os_pages = set(
    converter.address_to_pages(
        base_address,
        hot_bytes
    )
)


print(
    "\nHot logical pages:",
    HOT_PAGES
)

print(
    "Hot OS pages:",
    len(hot_os_pages)
)


# --------------------------------------------------
# Page-frequency analysis
# --------------------------------------------------

page_counts = Counter(
    access["page_id"]
    for access in page_trace
)


hot_accesses = sum(
    count
    for page, count in page_counts.items()
    if page in hot_os_pages
)


cold_accesses = (
    len(page_trace)
    - hot_accesses
)


hot_ratio = (
    hot_accesses
    / len(page_trace)
)


print(
    "\n========== HOT / COLD =========="
)

print(
    "Hot-region accesses:",
    hot_accesses
)

print(
    "Cold-region accesses:",
    cold_accesses
)

print(
    "Hot-region ratio:",
    f"{hot_ratio:.4f}"
)


# --------------------------------------------------
# Top pages
# --------------------------------------------------

print(
    "\n========== TOP 20 PAGES =========="
)

for page_id, count in page_counts.most_common(20):

    region_type = (
        "HOT"
        if page_id in hot_os_pages
        else "COLD"
    )

    ratio = (
        count
        / len(page_trace)
    )

    print(
        f"page={page_id:<8} "
        f"accesses={count:<8} "
        f"ratio={ratio:.4f} "
        f"{region_type}"
    )


# --------------------------------------------------
# Next-use-distance analysis
# --------------------------------------------------

labeler = NextUseLabeler(
    no_future_value=-1
)

labels = labeler.generate_labels(
    page_trace
)


distances = [
    item["next_use_distance"]
    for item in labels
]


never_used_again = sum(
    distance == -1
    for distance in distances
)


finite_distances = [
    distance
    for distance in distances
    if distance != -1
]


print(
    "\n========== NEXT USE =========="
)

print(
    "Never reused:",
    never_used_again
)


thresholds = [
    1,
    2,
    4,
    8,
    16,
    32,
    64,
    128,
    256,
    512,
    1024
]


for threshold in thresholds:

    count = sum(
        distance <= threshold
        for distance in finite_distances
    )

    ratio = (
        count
        / len(finite_distances)
        if finite_distances
        else 0.0
    )

    print(
        f"next_use <= {threshold:<4}: "
        f"{count:<8} "
        f"({ratio:.4f})"
    )


if finite_distances:

    sorted_distances = sorted(
        finite_distances
    )

    n = len(
        sorted_distances
    )

    def percentile(p):

        index = int(
            (n - 1) * p
        )

        return sorted_distances[
            index
        ]


    print(
        "\nMedian next-use:",
        percentile(0.50)
    )

    print(
        "P90 next-use:",
        percentile(0.90)
    )

    print(
        "P95 next-use:",
        percentile(0.95)
    )

    print(
        "P99 next-use:",
        percentile(0.99)
    )

    print(
        "Maximum next-use:",
        max(sorted_distances)
    )
