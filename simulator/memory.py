from simulator.replacement import LRUReplacement



class Memory:


    def __init__(self, capacity):

        self.capacity = capacity

        self.pages = []

        self.page_faults = 0

        self.time = 0

        self.replacement = LRUReplacement()



    def access(self,page):

        self.time += 1


        # Page موجود است
        if page in self.pages:

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
