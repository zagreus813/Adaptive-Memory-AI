from workloads.transformer import TransformerWorkload
from simulator.runner import WorkloadRunner


transformer = TransformerWorkload(
    tokens=6
)


runner = WorkloadRunner(
    workload=transformer,
    memory_size=5
)


result = runner.run()


print("\n==========")

print(
    "Metrics:",
    result["metrics"]
)


print(
    "Final Memory:",
    result["memory"]
)
