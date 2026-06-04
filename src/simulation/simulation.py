from simulation.core.fleet import Fleet
from simulation.core.vm import VM
from simulation.core.resource_set import ResourceSet
from simulation.policies.base import SchedulingPolicy
import random

class Simulation:
    def __init__(self, fleet: Fleet, vm_count: int, policy: SchedulingPolicy):
        self.fleet = fleet
        self.vm_count = vm_count
        self.policy = policy

    def run(self):
        vms = []
        for i in range(self.vm_count):
            vms.append(self.simulateVMRequest(i))

        self.fleet.schedule(vms, self.policy)

    def simulateVMRequest(self, vm_id: int) -> VM:
        seed = random.random()

        if seed <= 0.25:
            vm = VM(f'vm-{vm_id}', ResourceSet(cpu=1, memGB=0.5, diskGB=10))

        elif seed <= 0.50:
            vm = VM(f'vm-{vm_id}', ResourceSet(cpu=1, memGB=1, diskGB=25))

        elif seed <= 0.75:
            vm = VM(f'vm-{vm_id}', ResourceSet(cpu=1, memGB=2, diskGB=50))

        elif seed <= 0.87:
            vm = VM(f'vm-{vm_id}', ResourceSet(cpu=2, memGB=2, diskGB=60))

        elif seed <= 0.95:
            vm = VM(f'vm-{vm_id}', ResourceSet(cpu=2, memGB=4, diskGB=80))

        elif seed <= 0.99:
            vm = VM(f'vm-{vm_id}', ResourceSet(cpu=4, memGB=8, diskGB=160))

        else:
            vm = VM(f'vm-{vm_id}', ResourceSet(cpu=8, memGB=16, diskGB=320))

        return vm