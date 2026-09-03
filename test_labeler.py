from workloads.trace import AddressTraceWorkload
from ai.labeler import NextUseLabeler


workload = AddressTraceWorkload(
    "datasets/raw/sample_address_trace.csv"
)

trace = workload.generate_detailed()


labeler = NextUseLabeler()

labels = labeler.generate_labels(
    trace
)


for access, label in zip(trace, labels):

    print(
        f"t={access['timestamp']} "
        f"page={access['page_id']} "
        f"next_use={label['next_use_distance']}"
    )
