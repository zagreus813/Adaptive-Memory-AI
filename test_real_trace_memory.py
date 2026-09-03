from workloads.trace import AddressTraceWorkload
from simulator.runner import WorkloadRunner


workload = AddressTraceWorkload(
    filename="datasets/raw/sample_address_trace.csv",
    page_size=4096
)


runner = WorkloadRunner(
    workload=workload,
    memory_size=2
)


result = runner.run()


print("\n==========")
print("Workload:", workload.name)
print("Metrics:", result["metrics"])
print("Final Memory:", result["memory"])
