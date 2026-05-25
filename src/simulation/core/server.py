from simulation.core.vm import VM
from simulation.core.resource_set import ResourceSet

class Server:
    id: str
    capacity: ResourceSet

    scheduledVMs: dict[str, VM]

    def __init__(self, id: str, capacity: ResourceSet):
        self.id = id
        self.capacity = capacity
        self.scheduledVMs = {}

    def getUsedCapacity(self) -> ResourceSet:
        return sum((vm.desired for vm in self.scheduledVMs.values()), ResourceSet())

    def getAvailableCapacity(self) -> ResourceSet:
        return self.capacity - self.getUsedCapacity()

    def hasSpaceFor(self, requestedVM: VM) -> bool:
        return self.getAvailableCapacity().canFit(requestedVM.desired)

    def schedule(self, requestedVM: VM):
        if not self.hasSpaceFor(requestedVM):
            raise Exception('No space for additional VM')
        
        if self.scheduledVMs.get(requestedVM.id) is not None:
            raise Exception('Duplicate VM ID')
        
        self.scheduledVMs[requestedVM.id] = requestedVM
