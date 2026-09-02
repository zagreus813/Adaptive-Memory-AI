class Page:
    def __init__(self, page_id, process_id):
        self.page_id = page_id
        self.process_id = process_id
        
        self.access_count = 0
        
        self.last_access = 0


    def access(self, timestamp):
        self.access_count += 1
        self.last_access = timestamp


    def __repr__(self):
        return (
            f"Page(id={self.page_id}, "
            f"process={self.process_id}, "
            f"access={self.access_count})"
        )
