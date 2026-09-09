from traces.region import MemoryRegionLoader
from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter


TRACE_FILE = (
    "datasets/raw/valgrind/hot_cold.log"
)

META_FILE = (
    "datasets/raw/valgrind/hot_cold.meta"
)


# --------------------------------
# Load application memory region
# --------------------------------

region = MemoryRegionLoader.load(
    META_FILE
)


print(
    "Memory region:",
    region["base"],
    "->",
    region["end"]
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


# --------------------------------
# Address -> Page
# --------------------------------

converter = AddressConverter(
    page_size=4096
)


page_trace = converter.convert_trace(
    address_trace
)


unique_pages = sorted(
    {
        access["page_id"]
        for access in page_trace
    }
)


reads = sum(
    access["operation"] == "READ"
    for access in page_trace
)


writes = sum(
    access["operation"] == "WRITE"
    for access in page_trace
)


print()
print("Address accesses:", len(address_trace))
print("Page accesses:", len(page_trace))
print("Unique pages:", len(unique_pages))
print("Reads:", reads)
print("Writes:", writes)


print("\nFirst page:")
print(
    unique_pages[0],
    hex(unique_pages[0] * 4096)
)


print("\nLast page:")
print(
    unique_pages[-1],
    hex(unique_pages[-1] * 4096)
)
