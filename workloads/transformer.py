from workloads.base import Workload


class TransformerWorkload(Workload):


    def __init__(self, tokens=5):

        super().__init__(
            "Transformer_Inference"
        )

        self.tokens = tokens



    def generate(self):

        trace = []


        cache = []


        for token in range(self.tokens):

            # new KV cache page
            new_page = token


            cache.append(
                new_page
            )


            # access all KV cache
            trace.extend(
                cache
            )


        return trace
