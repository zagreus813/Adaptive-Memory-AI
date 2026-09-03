class PageStatistics:

    def __init__(self):
        self.access_count = 0
        self.read_count = 0
        self.write_count = 0

        self.last_access = None
        self.first_access = None


class FeatureExtractor:

    def __init__(self):
        self.pages = {}


    def _get_stats(self, page_id):

        if page_id not in self.pages:
            self.pages[page_id] = PageStatistics()

        return self.pages[page_id]


    def process_access(self, access):

        page_id = access["page_id"]
        timestamp = access["timestamp"]
        operation = access["operation"]

        stats = self._get_stats(page_id)

        # Feature must be calculated BEFORE updating
        # the state with the current access.
        if stats.last_access is None:
            time_since_last_access = -1
        else:
            time_since_last_access = (
                timestamp - stats.last_access
            )


        if stats.first_access is None:
            lifetime = 0
        else:
            lifetime = (
                timestamp - stats.first_access
            )


        if lifetime > 0:
            access_frequency = (
                stats.access_count / lifetime
            )
        else:
            access_frequency = 0.0


        features = {
            "timestamp": timestamp,
            "page_id": page_id,

            "access_count": stats.access_count,
            "read_count": stats.read_count,
            "write_count": stats.write_count,

            "time_since_last_access":
                time_since_last_access,

            "access_frequency":
                access_frequency
        }


        # --------------------------------
        # Update state AFTER feature extraction
        # --------------------------------

        if stats.first_access is None:
            stats.first_access = timestamp

        stats.access_count += 1

        if operation == "READ":
            stats.read_count += 1

        elif operation == "WRITE":
            stats.write_count += 1

        stats.last_access = timestamp


        return features
