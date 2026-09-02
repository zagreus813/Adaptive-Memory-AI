import csv


class MemoryLogger:


    def __init__(self, filename):

        self.filename = filename

        self.file = open(
            filename,
            "w",
            newline=""
        )


        self.writer = csv.writer(
            self.file
        )


        self.writer.writerow(
            [
                "timestamp",
                "page_id",
                "process_id",
                "operation"
            ]
        )


    def log(
        self,
        timestamp,
        page,
        operation="READ"
    ):

        self.writer.writerow(
            [
                timestamp,
                page.page_id,
                page.process_id,
                operation
            ]
        )



    def close(self):

        self.file.close()
