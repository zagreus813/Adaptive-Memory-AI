from traces.region import MemoryRegionLoader
from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter

from ai.eviction_dataset import EvictionDatasetBuilder


TRACE_FILE = (
    "datasets/raw/valgrind/"
    "hot_cold_train.log"
)

META_FILE = (
    "datasets/raw/valgrind/"
    "hot_cold_train.meta"
)

OUTPUT_FILE = (
    "datasets/processed/"
    "hot_cold_train_eviction_c16.csv"
)


PAGE_SIZE = 4096
TOTAL_PAGES = 256
INT_SIZE = 4
CAPACITY = 16


INIT_ACCESSES = (
    TOTAL_PAGES
    * PAGE_SIZE
    // INT_SIZE
)


# --------------------------------
# Load memory region
# --------------------------------

region = MemoryRegionLoader.load(
    META_FILE
)


# --------------------------------
# Parse Valgrind trace
# --------------------------------

parser = ValgrindTraceParser(
    min_address=region["base"],
    max_address=region["end"]
)


address_trace = parser.parse(
    TRACE_FILE
)


# Remove initialization phase.
measurement_trace = address_trace[
    INIT_ACCESSES:
]


# --------------------------------
# Address -> Page
# --------------------------------

converter = AddressConverter(
    page_size=PAGE_SIZE
)


page_trace = converter.convert_trace(
    measurement_trace
)


# --------------------------------
# Build training dataset
# --------------------------------

builder = EvictionDatasetBuilder(
    capacity=CAPACITY
)


summary = builder.build_to_csv(
    page_trace,
    OUTPUT_FILE
)


print(
    "========== TRAIN DATASET =========="
)

for key, value in summary.items():
    print(
        f"{key}: {value}"
    )


print(
    "\nOutput:",
    OUTPUT_FILE
)
