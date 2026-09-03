from workloads.trace import AddressTraceWorkload


workload = AddressTraceWorkload(
    "datasets/raw/sample_address_trace.csv"
)


trace = workload.generate_detailed()


for access in trace:
    print(access)
