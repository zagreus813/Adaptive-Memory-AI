from simulator.process import Process
from simulator.memory import Memory



memory = Memory(3)


process = Process(
    1,
    "CNN"
)


process.allocate_pages(5)



sequence = [
    0,
    1,
    2,
    0,
    3,
    4
]


for page_id in sequence:

    page = process.get_page(page_id)


    result = memory.access(page)


    print(
        "Access",
        page_id,
        "->",
        result
    )


print("\nFinal Memory:")
print(memory.status())


print(
    "Faults:",
    memory.page_faults
)
