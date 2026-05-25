from simulation.core.server import Server
from simulation.core.vm import VM
from simulation.core.resource_set import ResourceSet
from simulation.policies.base import SchedulingPolicy

class Fleet:
    servers: list[Server]

    def __init__(self, n_servers: int, server_capacity: ResourceSet):
        self.servers = []

        for i in range(n_servers):
            self.servers.append(Server(
                id=f'server-{i}',
                capacity=server_capacity
            ))

    def schedule(self, vm: VM, policy: SchedulingPolicy) -> str | None:
        return policy.place(vm, self.servers)
