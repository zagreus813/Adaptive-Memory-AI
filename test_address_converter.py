from traces.loader import AddressTraceLoader
from traces.converter import AddressConverter


loader = AddressTraceLoader(
    "datasets/raw/sample_address_trace.csv"
)

converter = AddressConverter(
    page_size=4096
)

trace = loader.load()

print("Raw accesses:", len(trace))

print("\nConverted trace:")

for access in trace:
    converted = converter.convert_access(access)

    print(
        access["address"],
        "-> Page",
        converted["page_id"],
        converted["operation"]
    )
