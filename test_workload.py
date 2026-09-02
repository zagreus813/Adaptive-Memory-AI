from workloads.cnn import CNNWorkload



cnn = CNNWorkload()


trace = cnn.generate()


print(
    cnn.name
)


print(trace)
