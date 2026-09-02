from workloads.transformer import TransformerWorkload


model = TransformerWorkload(
    tokens=6
)


trace = model.generate()


print(
    model.name
)


print(trace)
