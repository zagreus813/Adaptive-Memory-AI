class LRUReplacement:


    def select_victim(self, pages):

        if not pages:
            return None


        victim = min(
            pages,
            key=lambda page: page.last_access
        )


        return victim
