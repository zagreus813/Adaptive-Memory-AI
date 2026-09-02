from workloads.cnn import CNNWorkload
from simulator.runner import WorkloadRunner



cnn = CNNWorkload()


runner = WorkloadRunner(
    workload=cnn,
    memory_size=5
)


result = runner.run()



print("\n==========")

print(
    "Metrics:",
    result["metrics"]
)


print(
    "Page Faults:",
    result["metrics"]["faults"]
)


print(
    "Hit Ratio:",
    result["metrics"]["hit_ratio"]
)


print(
    "Final Memory:",
    result["memory"]
)
