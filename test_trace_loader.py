from traces.loader import TraceLoader


loader = TraceLoader(
    "results/memory_trace.csv"
)

trace = loader.load()

print("Loaded accesses:", len(trace))

for access in trace[:5]:
    print(access)
