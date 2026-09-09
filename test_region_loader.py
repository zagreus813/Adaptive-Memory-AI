from traces.region import MemoryRegionLoader


region = MemoryRegionLoader.load(
    "datasets/raw/valgrind/hot_cold.meta"
)

print(region)
