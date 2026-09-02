from simulator.process import Process
from simulator.memory import Memory



memory = Memory(capacity=3)


process = Process(
    pid=1,
    name="CNN_Workload"
)


process.allocate_pages(5)



print(process)



for page in process.pages:

    result = memory.load(page)

    print(
        "Loading:",
        page,
        "Success:",
        result
    )


print("\nMemory State:")
print(memory.status())


print(
    "Page Faults:",
    memory.page_faults
)
