import joblib
import pandas as pd

from ai.features import FeatureExtractor


class MemAISimulator:

    def __init__(
        self,
        capacity,
        model_path
    ):
        if capacity <= 0:
            raise ValueError(
                "capacity must be greater than zero"
            )

        self.capacity = capacity

        bundle = joblib.load(
            model_path
        )

        self.model = bundle["model"]
        self.features = bundle["features"]


    def run(self, trace):

        extractor = FeatureExtractor()

        resident = set()

        last_access = {}
        loaded_at = {}


        hits = 0
        faults = 0
        evictions = 0


        for access in trace:

            page_id = access["page_id"]
            timestamp = access["timestamp"]


            # ========================================
            # HIT
            # ========================================

            if page_id in resident:

                hits += 1


            # ========================================
            # MISS
            # ========================================

            else:

                faults += 1


                # ------------------------------------
                # Eviction required
                # ------------------------------------

                if len(resident) >= self.capacity:

                    evictions += 1


                    # LRU ordering is itself a feature.
                    #
                    # rank 0 = least recently used
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


                    candidate_rows = []
                    candidate_pages = []


                    for candidate in sorted(
                        resident
                    ):

                        snapshot = (
                            extractor.snapshot(
                                candidate,
                                timestamp
                            )
                        )


                        row = {
                            "access_count":
                                snapshot[
                                    "access_count"
                                ],

                            "read_count":
                                snapshot[
                                    "read_count"
                                ],

                            "write_count":
                                snapshot[
                                    "write_count"
                                ],

                            "time_since_last_access":
                                snapshot[
                                    "time_since_last_access"
                                ],

                            "access_frequency":
                                snapshot[
                                    "access_frequency"
                                ],

                            "mean_reuse_gap":
                                snapshot[
                                    "mean_reuse_gap"
                                ],

                            "read_ratio":
                                snapshot[
                                    "read_ratio"
                                ],

                            "write_ratio":
                                snapshot[
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
                                ]
                        }


                        candidate_rows.append(
                            row
                        )

                        candidate_pages.append(
                            candidate
                        )


                    # --------------------------------
                    # Predict next-use score
                    # --------------------------------

                    X = pd.DataFrame(
                        candidate_rows,
                        columns=self.features
                    )


                    scores = self.model.predict(
                        X
                    )


                    # Larger predicted next-use
                    # distance => better eviction
                    # candidate.
                    victim_index = int(
                        scores.argmax()
                    )


                    victim = candidate_pages[
                        victim_index
                    ]


                    resident.remove(
                        victim
                    )

                    del loaded_at[
                        victim
                    ]


                # ------------------------------------
                # Load current page
                # ------------------------------------

                resident.add(
                    page_id
                )

                loaded_at[
                    page_id
                ] = timestamp


            # ========================================
            # Update history AFTER making decision
            #
            # This is important:
            # the model must not observe the current
            # access before selecting the victim.
            # ========================================

            last_access[
                page_id
            ] = timestamp


            extractor.process_access(
                access
            )


        accesses = len(trace)


        return {
            "algorithm": "MemAI",
            "capacity": self.capacity,
            "accesses": accesses,
            "hits": hits,
            "faults": faults,
            "evictions": evictions,
            "hit_ratio": (
                hits / accesses
                if accesses
                else 0.0
            )
        }
