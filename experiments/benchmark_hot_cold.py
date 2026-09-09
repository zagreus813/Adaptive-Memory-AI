import csv
import os

from traces.region import MemoryRegionLoader
from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter

from simulator.trace_policies import (
    LRUSimulator,
    OPTSimulator
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
# Parse trace
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
# Convert to page trace
# --------------------------------

converter = AddressConverter(
    page_size=PAGE_SIZE
)


detailed_page_trace = (
    converter.convert_trace(
        measurement_trace
    )
)


page_trace = [
    access["page_id"]
    for access in detailed_page_trace
]


print(
    "Measurement accesses:",
    len(page_trace)
)

print(
    "Unique pages:",
    len(set(page_trace))
)


# --------------------------------
# Benchmark
# --------------------------------

capacities = [
    8,
    16,
    32,
    64
]


results = []


for capacity in capacities:

    print(
        f"\n========== Capacity {capacity} =========="
    )


    lru = LRUSimulator(
        capacity
    )

    opt = OPTSimulator(
        capacity
    )


    lru_result = lru.run(
        page_trace
    )

    opt_result = opt.run(
        page_trace
    )


    results.append(
        lru_result
    )

    results.append(
        opt_result
    )


    print(
        "LRU:",
        f"faults={lru_result['faults']}",
        f"hit_ratio={lru_result['hit_ratio']:.4f}"
    )


    print(
        "OPT:",
        f"faults={opt_result['faults']}",
        f"hit_ratio={opt_result['hit_ratio']:.4f}"
    )


    improvement_potential = (
        lru_result["faults"]
        - opt_result["faults"]
    )


    improvement_percent = (
        improvement_potential
        / lru_result["faults"]
        * 100
        if lru_result["faults"]
        else 0.0
    )


    print(
        "Maximum fault-reduction potential:",
        improvement_potential,
        f"({improvement_percent:.2f}%)"
    )


# --------------------------------
# Save CSV
# --------------------------------

os.makedirs(
    "results",
    exist_ok=True
)


output = (
    "results/"
    "hot_cold_lru_vs_opt.csv"
)


with open(
    output,
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "algorithm",
            "capacity",
            "accesses",
            "hits",
            "faults",
            "hit_ratio"
        ]
    )

    writer.writeheader()

    writer.writerows(
        results
    )


print(
    "\nResults saved:",
    output
)
