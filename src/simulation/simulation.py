from simulation.core.fleet import Fleet
from simulation.core.vm import VM
from simulation.core.resource_set import ResourceSet
from simulation.policies.base import SchedulingPolicy
import random
from dataclasses import dataclass

@dataclass
class SimulationResult:
    placements: list[tuple[str, str]]
    totalStranded: ResourceSet
    totalUnused: ResourceSet

class Simulation:
    def __init__(self, fleet: Fleet, vm_count: int, policy: SchedulingPolicy):
        self.fleet = fleet
        self.vm_count = vm_count
        self.policy = policy

    def run(self) -> SimulationResult:
        vms = []
        for i in range(self.vm_count):
            vms.append(self.simulateVMRequest(i))

        placements = self.fleet.schedule(vms, self.policy)

        totalStranded = ResourceSet()
        totalUnused = ResourceSet()

        for server in self.fleet.servers:
            available = server.getAvailableCapacity()

            totalUnused += available
            if available.hasStranded():
                totalStranded += available

        return SimulationResult(
            placements = placements,
            totalStranded = totalStranded,
            totalUnused = totalUnused
        )

    def simulateVMRequest(self, vm_id: int) -> VM:
        seed = random.random()

        if seed <= 0.25:
            vm = VM(f'{vm_id}', ResourceSet(cpu=1, memGB=0.5, diskGB=10))

        elif seed <= 0.50:
            vm = VM(f'{vm_id}', ResourceSet(cpu=1, memGB=1, diskGB=25))

        elif seed <= 0.75:
            vm = VM(f'{vm_id}', ResourceSet(cpu=2, memGB=1, diskGB=50))

        elif seed <= 0.87:
            vm = VM(f'{vm_id}', ResourceSet(cpu=2, memGB=1, diskGB=60))

        elif seed <= 0.95:
            vm = VM(f'{vm_id}', ResourceSet(cpu=4, memGB=1, diskGB=80))

        elif seed <= 0.99:
            vm = VM(f'{vm_id}', ResourceSet(cpu=8, memGB=1, diskGB=160))

        else:
            vm = VM(f'{vm_id}', ResourceSet(cpu=16, memGB=1, diskGB=320))

        return vm