from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM
from simulation.core.vm_placement import VMPlacement

class GoalProgrammingPolicy(SchedulingPolicy):
    def place(self, vms: list[VM], servers: list[Server]) -> list[VMPlacement]:
        raise NotImplementedError
