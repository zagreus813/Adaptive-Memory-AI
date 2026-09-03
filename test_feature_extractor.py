from workloads.trace import AddressTraceWorkload
from ai.features import FeatureExtractor


workload = AddressTraceWorkload(
    "datasets/raw/sample_address_trace.csv"
)

trace = workload.generate_detailed()


extractor = FeatureExtractor()


for access in trace:

    features = extractor.process_access(
        access
    )

    print(features)
