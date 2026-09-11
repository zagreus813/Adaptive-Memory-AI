import csv
import os

from collections import defaultdict
from collections import deque

from ai.features import FeatureExtractor


class EvictionDatasetBuilder:

    FIELDNAMES = [
        "decision_id",
        "timestamp",
        "capacity",
        "candidate_page_id",

        "access_count",
        "read_count",
        "write_count",

        "time_since_last_access",
        "access_frequency",
        "mean_reuse_gap",

        "read_ratio",
        "write_ratio",

        "resident_age",
        "lru_rank",

        "next_use_distance",
        "never_reused",
        "is_opt_victim"
    ]


    def __init__(
        self,
        capacity
    ):

        if capacity <= 0:
            raise ValueError(
                "capacity must be greater than zero"
            )

        self.capacity = capacity


    def build_to_csv(
        self,
        trace,
        filename
    ):

        if not trace:
            raise ValueError(
                "trace must not be empty"
            )


        # --------------------------------
        # Future occurrence index
        # --------------------------------

        future_positions = defaultdict(
            deque
        )


        for index, access in enumerate(trace):

            future_positions[
                access["page_id"]
            ].append(index)


        # --------------------------------
        # Online state
        # --------------------------------

        extractor = FeatureExtractor()

        resident = set()

        last_access = {}
        loaded_at = {}


        accesses = 0
        hits = 0
        faults = 0

        decisions = 0
        rows = 0


        no_future_distance = (
            len(trace) + 1
        )


        directory = os.path.dirname(
            filename
        )

        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )


        # --------------------------------
        # Stream directly to CSV
        # --------------------------------

        with open(
            filename,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES
            )

            writer.writeheader()


            for index, access in enumerate(trace):

                accesses += 1

                page_id = access["page_id"]
                timestamp = access["timestamp"]


                # Remove current occurrence from
                # future positions.
                queue = future_positions[
                    page_id
                ]

                if (
                    queue
                    and queue[0] == index
                ):
                    queue.popleft()


                # --------------------------------
                # HIT
                # --------------------------------

                if page_id in resident:

                    hits += 1


                # --------------------------------
                # MISS
                # --------------------------------

                else:

                    faults += 1


                    # ----------------------------
                    # Eviction required
                    # ----------------------------

                    if (
                        len(resident)
                        >= self.capacity
                    ):

                        decisions += 1


                        # LRU order:
                        # rank 0 = oldest page.
                        ordered_by_recency = sorted(
                            resident,
                            key=lambda page:
                                last_access[page]
                        )


                        lru_rank = {
                            page: rank
                            for rank, page
                            in enumerate(
                                ordered_by_recency
                            )
                        }


                        oracle_distance = {}


                        for candidate in resident:

                            candidate_future = (
                                future_positions[
                                    candidate
                                ]
                            )


                            if candidate_future:

                                distance = (
                                    candidate_future[0]
                                    - index
                                )

                                never_reused = 0

                            else:

                                distance = (
                                    no_future_distance
                                )

                                never_reused = 1


                            oracle_distance[
                                candidate
                            ] = (
                                distance,
                                never_reused
                            )


                        max_distance = max(
                            distance
                            for distance, _
                            in oracle_distance.values()
                        )


                        # ----------------------------
                        # Record every candidate.
                        # ----------------------------

                        for candidate in sorted(
                            resident
                        ):

                            features = (
                                extractor.snapshot(
                                    candidate,
                                    timestamp
                                )
                            )


                            (
                                distance,
                                never_reused
                            ) = oracle_distance[
                                candidate
                            ]


                            row = {
                                "decision_id":
                                    decisions,

                                "timestamp":
                                    timestamp,

                                "capacity":
                                    self.capacity,

                                "candidate_page_id":
                                    candidate,

                                "access_count":
                                    features[
                                        "access_count"
                                    ],

                                "read_count":
                                    features[
                                        "read_count"
                                    ],

                                "write_count":
                                    features[
                                        "write_count"
                                    ],

                                "time_since_last_access":
                                    features[
                                        "time_since_last_access"
                                    ],

                                "access_frequency":
                                    features[
                                        "access_frequency"
                                    ],

                                "mean_reuse_gap":
                                    features[
                                        "mean_reuse_gap"
                                    ],

                                "read_ratio":
                                    features[
                                        "read_ratio"
                                    ],

                                "write_ratio":
                                    features[
                                        "write_ratio"
                                    ],

                                "resident_age":
                                    (
                                        timestamp
                                        - loaded_at[
                                            candidate
                                        ]
                                    ),

                                "lru_rank":
                                    lru_rank[
                                        candidate
                                    ],

                                "next_use_distance":
                                    distance,

                                "never_reused":
                                    never_reused,

                                "is_opt_victim":
                                    int(
                                        distance
                                        == max_distance
                                    )
                            }


                            writer.writerow(
                                row
                            )

                            rows += 1


                        # ----------------------------
                        # Continue dataset collection
                        # using LRU as behavior policy.
                        # ----------------------------

                        victim = (
                            ordered_by_recency[0]
                        )

                        resident.remove(
                            victim
                        )

                        del loaded_at[
                            victim
                        ]


                    resident.add(
                        page_id
                    )

                    loaded_at[
                        page_id
                    ] = timestamp


                # --------------------------------
                # Update online history only AFTER
                # candidate features were created.
                # --------------------------------

                last_access[
                    page_id
                ] = timestamp


                extractor.process_access(
                    access
                )


        return {
            "accesses": accesses,
            "hits": hits,
            "faults": faults,
            "decisions": decisions,
            "rows": rows,
            "capacity": self.capacity
        }
