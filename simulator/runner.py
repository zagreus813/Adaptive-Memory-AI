from simulator.process import Process
from simulator.memory import Memory



class WorkloadRunner:


    def __init__(
        self,
        workload,
        memory_size=5
    ):

        self.workload = workload

        self.memory = Memory(
            memory_size,
            verbose=False

        )

        self.process = Process(
            pid=1,
            name=workload.name
        )


    def prepare(self):

        trace = self.workload.generate()


        max_page = max(trace)


        self.process.allocate_pages(
            max_page + 1
        )


        return trace



    def run(self):

        trace = self.prepare()


        for page_id in trace:

            page = self.process.get_page(
                page_id
            )

            result = self.memory.access(
                page
            )


            print(
                f"Page {page_id}: {result}"
            )


        self.memory.logger.close()

        return {
            "metrics": self.memory.metrics(),
            "memory": self.memory.status()
        }
