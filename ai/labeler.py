class NextUseLabeler:

    def __init__(self, no_future_value=-1):
        self.no_future_value = no_future_value


    def generate_labels(self, trace):

        labels = []

        # آخرین محل آینده هر page را
        # هنگام حرکت از انتهای trace نگه می‌داریم.
        next_position = {}

        for i in range(len(trace) - 1, -1, -1):

            page_id = trace[i]["page_id"]

            if page_id in next_position:

                distance = (
                    next_position[page_id] - i
                )

            else:

                distance = self.no_future_value


            labels.append({
                "timestamp": trace[i]["timestamp"],
                "page_id": page_id,
                "next_use_distance": distance
            })


            next_position[page_id] = i


        labels.reverse()

        return labels
