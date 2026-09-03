from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter


ARRAY_BASE = "0x40302a0"
ARRAY_END = "0x40342a0"


parser = ValgrindTraceParser(
    min_address=ARRAY_BASE,
    max_address=ARRAY_END
)


address_trace = parser.parse(
    "datasets/raw/valgrind/memory_walk.log"
)


converter = AddressConverter(
    page_size=4096
)


page_trace = converter.convert_trace(
    address_trace
)


print(
    "Address accesses:",
    len(address_trace)
)

print(
    "Page accesses:",
    len(page_trace)
)


unique_pages = sorted(
    set(
        x["page_id"]
        for x in page_trace
    )
)


print(
    "Unique pages:",
    len(unique_pages)
)


print("\nPages:")

for page in unique_pages:
    print(
        page,
        hex(page * 4096)
    )


print("\nFirst 20 page accesses:")

for access in page_trace[:20]:
    print(access)
