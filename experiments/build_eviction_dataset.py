from traces.region import MemoryRegionLoader
from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter

from ai.eviction_dataset import (
    EvictionDatasetBuilder
)


TRACE_FILE = (
    "datasets/raw/valgrind/hot_cold.log"
)

META_FILE = (
    "datasets/raw/valgrind/hot_cold.meta"
)


PAGE_SIZE = 4096

TOTAL_PAGES = 256

INT_SIZE = 4


INIT_ACCESSES = (
    TOTAL_PAGES
    * PAGE_SIZE
    // INT_SIZE
)


# --------------------------------
# Load region
# --------------------------------

region = MemoryRegionLoader.load(
    META_FILE
)


# --------------------------------
# Parse real trace
# --------------------------------

parser = ValgrindTraceParser(
    min_address=region["base"],
    max_address=region["end"]
)


address_trace = parser.parse(
    TRACE_FILE
)


measurement_trace = address_trace[
    INIT_ACCESSES:
]


# --------------------------------
# Address -> page
# --------------------------------

converter = AddressConverter(
    page_size=PAGE_SIZE
)


page_trace = converter.convert_trace(
    measurement_trace
)


# --------------------------------
# Build eviction-decision dataset
# --------------------------------

builder = EvictionDatasetBuilder(
    capacity=16
)


output = (
    "datasets/processed/"
    "hot_cold_eviction_c16.csv"
)


summary = builder.build_to_csv(
    page_trace,
    output
)


print(
    "========== EVICTION DATASET =========="
)

for key, value in summary.items():
    print(
        f"{key}: {value}"
    )


print(
    "\nOutput:",
    output
)
