from traces.valgrind_parser import ValgrindTraceParser


parser = ValgrindTraceParser()

trace = parser.parse(
    "datasets/raw/valgrind/memory_walk.log"
)


print(
    "Data memory accesses:",
    len(trace)
)


for access in trace[:20]:
    print(access)
