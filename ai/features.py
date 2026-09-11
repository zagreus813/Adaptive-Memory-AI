class PageStatistics:

    def __init__(self):
        self.access_count = 0

        self.read_count = 0
        self.write_count = 0

        self.first_access = None
        self.last_access = None

        self.reuse_count = 0
        self.total_reuse_gap = 0
        self.last_reuse_gap = None


class FeatureExtractor:

    def __init__(self):
        self.pages = {}


    def _get_stats(self, page_id):

        if page_id not in self.pages:
            self.pages[page_id] = PageStatistics()

        return self.pages[page_id]


    def snapshot(
        self,
        page_id,
        timestamp
    ):
        """
        Return features using ONLY information that
        existed before the current memory access.
        """

        stats = self._get_stats(
            page_id
        )


        if stats.last_access is None:
            time_since_last_access = -1
        else:
            time_since_last_access = (
                timestamp
                - stats.last_access
            )


        if stats.first_access is None:
            lifetime = 0
        else:
            lifetime = (
                timestamp
                - stats.first_access
            )


        if lifetime > 0:

            access_frequency = (
                stats.access_count
                / lifetime
            )

        else:

            access_frequency = 0.0


        if stats.reuse_count > 0:

            mean_reuse_gap = (
                stats.total_reuse_gap
                / stats.reuse_count
            )

        else:

            mean_reuse_gap = -1.0


        if stats.access_count > 0:

            read_ratio = (
                stats.read_count
                / stats.access_count
            )

            write_ratio = (
                stats.write_count
                / stats.access_count
            )

        else:

            read_ratio = 0.0
            write_ratio = 0.0


        return {
            "timestamp":
                timestamp,

            "page_id":
                page_id,

            "access_count":
                stats.access_count,

            "read_count":
                stats.read_count,

            "write_count":
                stats.write_count,

            "time_since_last_access":
                time_since_last_access,

            "access_frequency":
                access_frequency,

            "mean_reuse_gap":
                mean_reuse_gap,

            "read_ratio":
                read_ratio,

            "write_ratio":
                write_ratio
        }


    def process_access(
        self,
        access
    ):
        """
        Generate the pre-access feature snapshot,
        then update the historical state.
        """

        page_id = access["page_id"]
        timestamp = access["timestamp"]
        operation = access["operation"]


        features = self.snapshot(
            page_id,
            timestamp
        )


        stats = self._get_stats(
            page_id
        )


        if stats.first_access is None:
            stats.first_access = timestamp


        if stats.last_access is not None:

            gap = (
                timestamp
                - stats.last_access
            )

            stats.total_reuse_gap += gap
            stats.reuse_count += 1
            stats.last_reuse_gap = gap


        stats.access_count += 1


        if operation == "READ":
            stats.read_count += 1

        elif operation == "WRITE":
            stats.write_count += 1


        stats.last_access = timestamp


        return features
