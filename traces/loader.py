import csv


class TraceLoader:

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        trace = []

        with open(self.filename, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                trace.append({
                    "timestamp": int(row["timestamp"]),
                    "page_id": int(row["page_id"]),
                    "process_id": int(row["process_id"]),
                    "operation": row["operation"]
                })

        return trace

class AddressTraceLoader:

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        trace = []

        with open(self.filename, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                trace.append({
                    "timestamp": int(row["timestamp"]),
                    "address": row["address"],
                    "process_id": int(row["process_id"]),
                    "operation": row["operation"]
                })

        return trace
