from abc import ABC, abstractmethod
from simulation.core.server import Server
from simulation.core.vm import VM
from simulation.core.vm_placement import VMPlacement

class SchedulingPolicy(ABC):
    @abstractmethod
    def place(self, vms: list[VM], servers: list[Server]) -> list[VMPlacement]:
        pass
