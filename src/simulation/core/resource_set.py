from dataclasses import dataclass

@dataclass
class ResourceSet:
    cpu: int = 0
    memGB: int = 0
    diskGB: int = 0

    def canFit(self, other: ResourceSet) -> bool:
        return (
            self.cpu >= other.cpu and
            self.memGB >= other.memGB and
            self.diskGB >= other.diskGB
        )

    def hasStranded(self) -> bool:
        return self.cpu == 0 or self.memGB == 0 or self.diskGB == 0

    def __add__(self, other):
        if not isinstance(other, ResourceSet):
            return NotImplemented

        return ResourceSet(
            self.cpu + other.cpu,
            self.memGB + other.memGB,
            self.diskGB + other.diskGB
        )

    def __sub__(self, other):
        if not isinstance(other, ResourceSet):
            return NotImplemented

        return ResourceSet(
            self.cpu - other.cpu,
            self.memGB - other.memGB,
            self.diskGB - other.diskGB
        )

    def __radd__(self, other):
        # enables sum([...])
        if other == 0:
            return self
        if isinstance(other, ResourceSet):
            return self + other
        return NotImplemented