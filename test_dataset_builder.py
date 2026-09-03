from workloads.trace import AddressTraceWorkload
from ai.dataset import DatasetBuilder


workload = AddressTraceWorkload(
    "datasets/raw/sample_address_trace.csv"
)


trace = workload.generate_detailed()


builder = DatasetBuilder(
    prediction_horizon=32
)


dataset = builder.build(trace)


builder.save(
    dataset,
    "datasets/processed/sample_training.csv"
)


for row in dataset:
    print(row)


print(
    "\nDataset rows:",
    len(dataset)
)
