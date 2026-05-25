from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM
from simulation.core.vm_placement import VMPlacement

class FirstFitPolicy(SchedulingPolicy):
    def place(self, vms: list[VM], servers: list[Server]) -> list[VMPlacement]:
        results = []

        for vm in vms:
            for server in servers:
                if server.hasSpaceFor(vm):
                    server.schedule(vm)
                    results.append(VMPlacement(vm.id, server.id))
                    break

            results.append(VMPlacement(vm.id, None))

        return results
