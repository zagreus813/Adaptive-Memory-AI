from traces.valgrind_parser import ValgrindTraceParser
from traces.converter import AddressConverter

from ai.dataset import DatasetBuilder


ARRAY_BASE = "0x40302a0"
ARRAY_END = "0x40342a0"


# --------------------------------
# Parse real Valgrind trace
# --------------------------------

parser = ValgrindTraceParser(
    min_address=ARRAY_BASE,
    max_address=ARRAY_END
)


address_trace = parser.parse(
    "datasets/raw/valgrind/memory_walk.log"
)


# --------------------------------
# Address -> Page
# --------------------------------

converter = AddressConverter(
    page_size=4096
)


page_trace = converter.convert_trace(
    address_trace
)


# --------------------------------
# Feature + Label generation
# --------------------------------

builder = DatasetBuilder(
    prediction_horizon=32
)


dataset = builder.build(
    page_trace
)


# --------------------------------
# Save
# --------------------------------

output = (
    "datasets/processed/"
    "memory_walk_training.csv"
)


builder.save(
    dataset,
    output
)


print(
    "Address accesses:",
    len(address_trace)
)

print(
    "Page accesses:",
    len(page_trace)
)

print(
    "Dataset rows:",
    len(dataset)
)

print(
    "Output:",
    output
)
