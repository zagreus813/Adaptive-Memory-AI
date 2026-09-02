import csv
import os

from workloads.cnn import CNNWorkload
from workloads.transformer import TransformerWorkload

from simulator.runner import WorkloadRunner



class Benchmark:


    def __init__(self):

        self.results = []



    def run_workload(
        self,
        workload,
        memory_size=5
    ):

        runner = WorkloadRunner(
            workload=workload,
            memory_size=memory_size
        )


        result = runner.run()


        metrics = result["metrics"]


        self.results.append(
            {
                "workload": workload.name,
                "algorithm": "LRU",
                "accesses": metrics["accesses"],
                "hits": metrics["hits"],
                "faults": metrics["faults"],
                "hit_ratio": metrics["hit_ratio"]
            }
        )



    def save(self, filename):

        os.makedirs(
            "results",
            exist_ok=True
        )


        with open(
            filename,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.results[0].keys()
            )


            writer.writeheader()

            writer.writerows(
                self.results
            )



if __name__ == "__main__":


    benchmark = Benchmark()


    workloads = [

        CNNWorkload(),

        TransformerWorkload(
            tokens=6
        )

    ]


    for workload in workloads:

        print(
            "\nRunning:",
            workload.name
        )


        benchmark.run_workload(
            workload
        )


    benchmark.save(
        "results/benchmark.csv"
    )


    print(
        "\nBenchmark finished."
    )
