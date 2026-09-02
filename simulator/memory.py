from simulator.replacement import LRUReplacement
from simulator.logger import MemoryLogger


class Memory:


    def __init__(self, capacity, verbose=True):
        self.capacity = capacity

        self.pages = []

        self.page_faults = 0

        self.time = 0

        self.replacement = LRUReplacement()

        self.logger = MemoryLogger(
           "results/memory_trace.csv"
        )
        self.hits = 0
        self.accesses = 0
        self.verbose = verbose

    def access(self,page):

        self.time += 1
        self.accesses += 1

        self.logger.log(
            self.time,
            page
        )
        # Page موجود است
        if page in self.pages:
        
            self.hits += 1

            page.access(self.time)

            return "HIT"



        # Page جدید
        self.page_faults += 1


        if len(self.pages) < self.capacity:

            self.pages.append(page)

            page.access(self.time)

            return "MISS"



        # Memory full
        victim = self.replacement.select_victim(
            self.pages
        )


        self.pages.remove(victim)


        self.pages.append(page)


        page.access(self.time)


        return f"REPLACE {victim}"



    def status(self):

        return self.pages
    def metrics(self):

        hit_ratio = 0

        if self.accesses > 0:
            hit_ratio = self.hits / self.accesses


        return {
            "accesses": self.accesses,
            "hits": self.hits,
            "faults": self.page_faults,
            "hit_ratio": hit_ratio
        }
