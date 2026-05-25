from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM

class GoalProgrammingPolicy(SchedulingPolicy):
    def place(self, vm: VM, servers: list[Server]) -> str | None:
        raise NotImplementedError
