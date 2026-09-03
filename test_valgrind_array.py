from traces.valgrind_parser import ValgrindTraceParser


ARRAY_BASE = "0x40302a0"
ARRAY_END = "0x40342a0"


parser = ValgrindTraceParser(
    min_address=ARRAY_BASE,
    max_address=ARRAY_END
)


trace = parser.parse(
    "datasets/raw/valgrind/memory_walk.log"
)


stats = parser.stats(trace)


print("========== Array Trace ==========")

print(
    "Memory range:",
    ARRAY_BASE,
    "->",
    ARRAY_END
)

print(
    "Array memory accesses:",
    stats["accesses"]
)

print(
    "Reads:",
    stats["reads"]
)

print(
    "Writes:",
    stats["writes"]
)


print("\nFirst 20 accesses:")

for access in trace[:20]:
    print(access)
