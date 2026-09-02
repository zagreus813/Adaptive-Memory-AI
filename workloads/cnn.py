from workloads.base import Workload
import random



class CNNWorkload(Workload):


    def __init__(self, layers=5):

        super().__init__(
            "CNN_Inference"
        )

        self.layers = layers



    def generate(self):

        trace = []


        for layer in range(self.layers):

            start = layer * 10


            # simulate layer memory reuse
            pages = [
                start,
                start+1,
                start+2,
                start+1,
                start
            ]


            trace.extend(pages)


        return trace
