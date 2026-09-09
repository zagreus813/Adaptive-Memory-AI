from collections import defaultdict, deque
from math import inf


class LRUSimulator:

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError(
                "capacity must be greater than zero"
            )

        self.capacity = capacity


    def run(self, trace):

        resident = set()
        last_access = {}

        hits = 0
        faults = 0

        for timestamp, page_id in enumerate(trace):

            if page_id in resident:

                hits += 1

            else:

                faults += 1

                if len(resident) >= self.capacity:

                    victim = min(
                        resident,
                        key=lambda page:
                            last_access[page]
                    )

                    resident.remove(victim)

                resident.add(page_id)

            last_access[page_id] = timestamp


        accesses = len(trace)

        return {
            "algorithm": "LRU",
            "capacity": self.capacity,
            "accesses": accesses,
            "hits": hits,
            "faults": faults,
            "hit_ratio": (
                hits / accesses
                if accesses
                else 0.0
            )
        }


class OPTSimulator:

    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError(
                "capacity must be greater than zero"
            )

        self.capacity = capacity


    def run(self, trace):

        future_positions = defaultdict(deque)

        # Pre-compute every future occurrence.
        for index, page_id in enumerate(trace):
            future_positions[page_id].append(index)


        resident = set()

        hits = 0
        faults = 0


        for index, page_id in enumerate(trace):

            # Remove the current occurrence.
            positions = future_positions[page_id]

            if (
                positions
                and positions[0] == index
            ):
                positions.popleft()


            if page_id in resident:

                hits += 1
                continue


            faults += 1


            if len(resident) >= self.capacity:

                victim = None
                farthest_next_use = -1


                for candidate in resident:

                    candidate_future = (
                        future_positions[candidate]
                    )


                    if candidate_future:

                        next_use = (
                            candidate_future[0]
                        )

                    else:

                        next_use = inf


                    if next_use > farthest_next_use:

                        farthest_next_use = next_use
                        victim = candidate


                resident.remove(victim)


            resident.add(page_id)


        accesses = len(trace)

        return {
            "algorithm": "OPT",
            "capacity": self.capacity,
            "accesses": accesses,
            "hits": hits,
            "faults": faults,
            "hit_ratio": (
                hits / accesses
                if accesses
                else 0.0
            )
        }
