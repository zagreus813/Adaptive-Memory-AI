from simulator.page import Page


class Process:

    def __init__(self, pid, name):
        self.pid = pid
        self.name = name
        
        self.pages = []


    def allocate_pages(self, number):

        for i in range(number):
            page = Page(
                page_id=len(self.pages),
                process_id=self.pid
            )

            self.pages.append(page)


    def get_page(self, page_id):
        return self.pages[page_id]


    def __repr__(self):
        return (
            f"Process(pid={self.pid}, "
            f"name={self.name}, "
            f"pages={len(self.pages)})"
        )
