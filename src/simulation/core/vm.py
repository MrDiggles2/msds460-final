from simulation.core.resource_set import ResourceSet

class VM:
    id: str
    desired: ResourceSet

    def __init__(self, id: str, desired: ResourceSet):
        self.id = id
        self.desired = desired
