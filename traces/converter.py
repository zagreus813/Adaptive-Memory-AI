class AddressConverter:

    def __init__(self, page_size=4096):
        if page_size <= 0:
            raise ValueError(
                "page_size must be greater than zero"
            )

        self.page_size = page_size


    @staticmethod
    def _normalize_address(address):

        if isinstance(address, int):
            return address

        if isinstance(address, str):
            return int(address, 16)

        raise TypeError(
            f"Unsupported address type: {type(address)}"
        )


    def address_to_page(self, address):
        """
        Convert one virtual address to its page ID.
        """

        address = self._normalize_address(
            address
        )

        return address // self.page_size


    def address_to_pages(
        self,
        address,
        size=1
    ):
        """
        Return every page touched by a memory access.

        Example:

            address = 0x1FFF
            size    = 8

        touches:

            page 1
            page 2
        """

        address = self._normalize_address(
            address
        )

        if size <= 0:
            raise ValueError(
                "access size must be greater than zero"
            )

        start_page = (
            address // self.page_size
        )

        end_address = (
            address + size - 1
        )

        end_page = (
            end_address // self.page_size
        )

        return list(
            range(
                start_page,
                end_page + 1
            )
        )


    def convert_access(self, access):
        """
        Backward-compatible conversion.

        Returns the page containing the first byte
        of an access.
        """

        page_id = self.address_to_page(
            access["address"]
        )

        return {
            "timestamp": access["timestamp"],
            "address": access["address"],
            "page_id": page_id,
            "process_id": access.get(
                "process_id",
                1
            ),
            "operation": access["operation"]
        }


    def convert_trace(self, trace):
        """
        Convert a complete address-level trace into
        a page-level trace.

        An address access spanning multiple pages
        generates one page access per touched page.
        """

        page_trace = []

        logical_timestamp = 0

        for access in trace:

            pages = self.address_to_pages(
                access["address"],
                access.get("size", 1)
            )

            for page_id in pages:

                logical_timestamp += 1

                page_trace.append({
                    "timestamp":
                        logical_timestamp,

                    "source_timestamp":
                        access["timestamp"],

                    "page_id":
                        page_id,

                    "process_id":
                        access.get(
                            "process_id",
                            1
                        ),

                    "operation":
                        access["operation"]
                })

        return page_trace
