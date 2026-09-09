class MemoryRegionLoader:

    @staticmethod
    def load(filename):

        base = None
        end = None


        with open(filename, "r") as file:

            for line in file:

                line = line.strip()


                if line.startswith(
                    "ARRAY_BASE="
                ):
                    base = line.split(
                        "=",
                        1
                    )[1]


                elif line.startswith(
                    "ARRAY_END="
                ):
                    end = line.split(
                        "=",
                        1
                    )[1]


        if base is None:
            raise ValueError(
                "ARRAY_BASE not found"
            )


        if end is None:
            raise ValueError(
                "ARRAY_END not found"
            )


        return {
            "base": base,
            "end": end
        }
