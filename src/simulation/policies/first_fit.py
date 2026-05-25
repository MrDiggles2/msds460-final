from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM

class FirstFitPolicy(SchedulingPolicy):
    def place(self, vm: VM, servers: list[Server]) -> str | None:
        for server in servers:
            if server.hasSpaceFor(vm):
                server.schedule(vm)
                return server.id

        return None
