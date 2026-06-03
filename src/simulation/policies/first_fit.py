from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM

class FirstFitPolicy(SchedulingPolicy):
    def place(self, vms: list[VM], servers: list[Server]):
        for vm in vms:
            for server in servers:
                if server.hasSpaceFor(vm):
                    server.schedule(vm)
                    break
