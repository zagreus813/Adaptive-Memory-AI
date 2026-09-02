from abc import ABC, abstractmethod


class Workload(ABC):


    def __init__(self, name):
        self.name = name



    @abstractmethod
    def generate(self):
        pass
