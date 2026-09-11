import csv
import os

from traces.region import MemoryRegionLoader
from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter

from simulator.trace_policies import (
    LRUSimulator,
    OPTSimulator
)

from simulator.memai_policy import (
    MemAISimulator
)


TRACE_FILE = (
    "datasets/raw/valgrind/"
    "hot_cold_test.log"
)

META_FILE = (
    "datasets/raw/valgrind/"
    "hot_cold_test.meta"
)

MODEL_FILE = (
    "models/"
    "memai_rf_hotcold_train_c16.joblib"
)


OUTPUT_FILE = (
    "results/"
    "memai_unseen_test.csv"
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


print(
    "========== UNSEEN TEST TRACE =========="
)


# --------------------------------------------------
# Load test memory region
# --------------------------------------------------

region = MemoryRegionLoader.load(
    META_FILE
)


print(
    "Region:",
    region["base"],
    "->",
    region["end"]
)


# --------------------------------------------------
# Parse TEST trace
# --------------------------------------------------

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


# --------------------------------------------------
# Address -> Page
# --------------------------------------------------

converter = AddressConverter(
    page_size=PAGE_SIZE
)


detailed_trace = converter.convert_trace(
    measurement_trace
)


page_trace = [
    access["page_id"]
    for access in detailed_trace
]


print(
    "Measurement accesses:",
    len(page_trace)
)

print(
    "Unique pages:",
    len(set(page_trace))
)


# --------------------------------------------------
# LRU
# --------------------------------------------------

print(
    "\nRunning LRU..."
)


lru = LRUSimulator(
    CAPACITY
)


lru_result = lru.run(
    page_trace
)


# --------------------------------------------------
# OPT
# --------------------------------------------------

print(
    "Running OPT..."
)


opt = OPTSimulator(
    CAPACITY
)


opt_result = opt.run(
    page_trace
)


# --------------------------------------------------
# MemAI
# --------------------------------------------------

print(
    "Running MemAI..."
)


memai = MemAISimulator(
    capacity=CAPACITY,
    model_path=MODEL_FILE
)


memai_result = memai.run(
    detailed_trace
)


# --------------------------------------------------
# Results
# --------------------------------------------------

print(
    "\n========== ONLINE RESULTS =========="
)


print(
    "LRU:"
)

print(
    f"  faults    = {lru_result['faults']}"
)

print(
    f"  hits      = {lru_result['hits']}"
)

print(
    f"  hit ratio = {lru_result['hit_ratio']:.6f}"
)


print(
    "\nMemAI:"
)

print(
    f"  faults    = {memai_result['faults']}"
)

print(
    f"  hits      = {memai_result['hits']}"
)

print(
    f"  hit ratio = {memai_result['hit_ratio']:.6f}"
)


print(
    "\nOPT:"
)

print(
    f"  faults    = {opt_result['faults']}"
)

print(
    f"  hits      = {opt_result['hits']}"
)

print(
    f"  hit ratio = {opt_result['hit_ratio']:.6f}"
)


# --------------------------------------------------
# MemAI improvement
# --------------------------------------------------

fault_reduction = (
    lru_result["faults"]
    - memai_result["faults"]
)


fault_reduction_percent = (
    fault_reduction
    / lru_result["faults"]
    * 100
    if lru_result["faults"]
    else 0.0
)


available_gap = (
    lru_result["faults"]
    - opt_result["faults"]
)


gap_closed_percent = (
    fault_reduction
    / available_gap
    * 100
    if available_gap > 0
    else 0.0
)


print(
    "\n========== IMPROVEMENT =========="
)


print(
    "Fault reduction vs LRU:",
    fault_reduction
)


print(
    "Fault reduction percent:",
    f"{fault_reduction_percent:.2f}%"
)


print(
    "LRU-to-OPT gap closed:",
    f"{gap_closed_percent:.2f}%"
)


# --------------------------------------------------
# Save
# --------------------------------------------------

results = [
    lru_result,
    memai_result,
    opt_result
]


os.makedirs(
    "results",
    exist_ok=True
)


fieldnames = [
    "algorithm",
    "capacity",
    "accesses",
    "hits",
    "faults",
    "hit_ratio"
]


with open(
    OUTPUT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames,
        extrasaction="ignore"
    )

    writer.writeheader()

    writer.writerows(
        results
    )


print(
    "\nResults saved:",
    OUTPUT_FILE
)
