import re


class ValgrindTraceParser:
    """
    Parser for Valgrind Lackey memory traces.

    Supported operations:
        I -> Instruction fetch
        L -> Memory read
        S -> Memory write
        M -> Memory modify

    Example Lackey lines:

        I  04001100,3
         L 0402de68,8
         S 1ffefff9c8,8
         M 040302a0,4
    """

    TRACE_PATTERN = re.compile(
        r"^\s*([ILSM])\s+([0-9a-fA-F]+),(\d+)"
    )

    def __init__(
        self,
        include_instructions=False,
        min_address=None,
        max_address=None
    ):
        self.include_instructions = include_instructions

        self.min_address = self._normalize_address(
            min_address
        )

        self.max_address = self._normalize_address(
            max_address
        )

    @staticmethod
    def _normalize_address(address):
        """
        Convert address to integer.

        Supports:

            0x40302a0
            "0x40302a0"
            "40302a0"
            None
        """

        if address is None:
            return None

        if isinstance(address, int):
            return address

        if isinstance(address, str):
            address = address.strip()

            if address.lower().startswith("0x"):
                return int(address, 16)

            return int(address, 16)

        raise TypeError(
            f"Unsupported address type: {type(address)}"
        )

    def _address_allowed(self, address):
        """
        Check whether an address belongs to the configured
        memory region.

        Range semantics:

            min_address <= address < max_address
        """

        if (
            self.min_address is not None
            and address < self.min_address
        ):
            return False

        if (
            self.max_address is not None
            and address >= self.max_address
        ):
            return False

        return True

    @staticmethod
    def _convert_operation(op):
        """
        Convert Valgrind Lackey operation to the internal
        MemAI representation.
        """

        if op == "L":
            return "READ"

        if op == "S":
            return "WRITE"

        if op == "M":
            # Lackey's M means the location is both
            # read and modified.
            #
            # For the current page-residency model,
            # represent it as one write-capable access.
            return "WRITE"

        if op == "I":
            return "INSTRUCTION"

        raise ValueError(
            f"Unknown Valgrind operation: {op}"
        )

    def parse(self, filename):
        """
        Parse a Valgrind Lackey trace.

        Returns a list such as:

        [
            {
                "timestamp": 1,
                "address": "0x40302a0",
                "size": 4,
                "process_id": 1,
                "operation": "WRITE"
            },
            ...
        ]
        """

        trace = []

        timestamp = 0

        with open(
            filename,
            "r",
            errors="ignore"
        ) as file:

            for line in file:

                match = self.TRACE_PATTERN.match(
                    line
                )

                # Ignore Valgrind metadata and
                # non-memory-trace lines.
                if not match:
                    continue

                op, address_text, size_text = (
                    match.groups()
                )

                # Ignore instruction fetches unless
                # explicitly requested.
                if (
                    op == "I"
                    and not self.include_instructions
                ):
                    continue

                address = int(
                    address_text,
                    16
                )

                size = int(
                    size_text
                )

                # Optional memory-region filtering.
                if not self._address_allowed(address):
                    continue

                timestamp += 1

                operation = (
                    self._convert_operation(op)
                )

                trace.append(
                    {
                        "timestamp": timestamp,
                        "address": hex(address),
                        "size": size,
                        "process_id": 1,
                        "operation": operation
                    }
                )

        return trace

    def stats(self, trace):
        """
        Generate simple statistics for a parsed trace.
        """

        reads = 0
        writes = 0
        instructions = 0

        for access in trace:

            operation = access["operation"]

            if operation == "READ":
                reads += 1

            elif operation == "WRITE":
                writes += 1

            elif operation == "INSTRUCTION":
                instructions += 1

        return {
            "accesses": len(trace),
            "reads": reads,
            "writes": writes,
            "instructions": instructions
        }
