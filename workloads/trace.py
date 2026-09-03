from workloads.base import Workload
from traces.loader import AddressTraceLoader
from traces.converter import AddressConverter


class AddressTraceWorkload(Workload):

    def __init__(
        self,
        filename,
        page_size=4096,
        name="Real_Address_Trace"
    ):
        super().__init__(name)

        self.filename = filename
        self.page_size = page_size


    def generate(self):

        loader = AddressTraceLoader(
            self.filename
        )

        converter = AddressConverter(
            page_size=self.page_size
        )

        raw_trace = loader.load()

        page_trace = []

        for access in raw_trace:

            converted = converter.convert_access(
                access
            )

            page_trace.append(
                converted["page_id"]
            )

        return page_trace
    def generate_detailed(self):

        loader = AddressTraceLoader(
            self.filename
        )

        converter = AddressConverter(
            page_size=self.page_size
        )

        raw_trace = loader.load()

        trace = []

        for access in raw_trace:
    
            converted = converter.convert_access(
                access
            )

            trace.append({
                "timestamp": converted["timestamp"],
                "page_id": converted["page_id"],
                "process_id": converted["process_id"],
                "operation": converted["operation"]
            })

        return trace
