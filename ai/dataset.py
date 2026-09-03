import csv
import os

from ai.features import FeatureExtractor
from ai.labeler import NextUseLabeler


class DatasetBuilder:

    def __init__(self, prediction_horizon=32):
        self.prediction_horizon = prediction_horizon


    def build(self, trace):

        extractor = FeatureExtractor()

        labeler = NextUseLabeler(
            no_future_value=-1
        )

        labels = labeler.generate_labels(trace)

        dataset = []

        for access, label in zip(trace, labels):

            features = extractor.process_access(
                access
            )

            distance = label["next_use_distance"]

            # Page is never reused again
            if distance == -1:
                target = self.prediction_horizon + 1

            # Reuse exists, but is outside prediction horizon
            elif distance > self.prediction_horizon:
                target = self.prediction_horizon + 1

            else:
                target = distance


            row = {
                "timestamp": features["timestamp"],
                "page_id": features["page_id"],

                "access_count":
                    features["access_count"],

                "read_count":
                    features["read_count"],

                "write_count":
                    features["write_count"],

                "time_since_last_access":
                    features["time_since_last_access"],

                "access_frequency":
                    features["access_frequency"],

                "is_write":
                    1 if access["operation"] == "WRITE" else 0,

                "next_use_distance":
                    target
            }

            dataset.append(row)

        return dataset


    def save(self, dataset, filename):

        if not dataset:
            return

        directory = os.path.dirname(filename)

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        with open(
            filename,
            "w",
            newline=""
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=dataset[0].keys()
            )

            writer.writeheader()

            writer.writerows(dataset)
