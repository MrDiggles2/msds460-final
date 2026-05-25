from abc import ABC, abstractmethod
from simulation.core.server import Server
from simulation.core.vm import VM

class SchedulingPolicy(ABC):
    @abstractmethod
    def place(self, vm: VM, servers: list[Server]) -> str | None:
        pass
