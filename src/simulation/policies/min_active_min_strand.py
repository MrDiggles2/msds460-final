from ortools.sat.python import cp_model

from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM


class MinActiveMinStrand(SchedulingPolicy):
    def place(self, vms: list[VM], servers: list[Server]):
        model = cp_model.CpModel()

        vm_keys = list(range(len(vms)))
        server_keys = list(range(len(servers)))

        ########################################################################
        # SCALE FLOATS → INTS
        ########################################################################

        SCALE = 100

        def s(x: float) -> int:
            return int(round(x * SCALE))

        ########################################################################
        # Decision variables
        ########################################################################

        x = {}
        for i in vm_keys:
            for j in server_keys:
                x[(i, j)] = model.NewBoolVar(f"x_{i}_{j}")

        # reject variable
        r = {}
        for i in vm_keys:
            r[i] = model.NewBoolVar(f"reject_{i}")

        y = {}
        for j in server_keys:
            y[j] = model.NewBoolVar(f"y_{j}")

        ########################################################################
        # Each VM is either assigned OR rejected
        ########################################################################

        for i in vm_keys:
            model.Add(sum(x[(i, j)] for j in server_keys) + r[i] == 1)

        ########################################################################
        # Capacity constraints
        ########################################################################

        for j, server in enumerate(servers):
            cap = server.capacity

            cpu_used = sum(s(vms[i].desired.cpu) * x[(i, j)] for i in vm_keys)
            mem_used = sum(s(vms[i].desired.memGB) * x[(i, j)] for i in vm_keys)
            disk_used = sum(s(vms[i].desired.diskGB) * x[(i, j)] for i in vm_keys)

            model.Add(cpu_used <= s(cap.cpu)).OnlyEnforceIf(y[j])
            model.Add(mem_used <= s(cap.memGB)).OnlyEnforceIf(y[j])
            model.Add(disk_used <= s(cap.diskGB)).OnlyEnforceIf(y[j])

            model.Add(cpu_used == 0).OnlyEnforceIf(y[j].Not())
            model.Add(mem_used == 0).OnlyEnforceIf(y[j].Not())
            model.Add(disk_used == 0).OnlyEnforceIf(y[j].Not())

        ########################################################################
        # Unused resources
        ########################################################################

        unused_cpu = {}
        unused_mem = {}
        unused_disk = {}

        for j, server in enumerate(servers):
            cap = server.capacity

            used_cpu = sum(s(vms[i].desired.cpu) * x[(i, j)] for i in vm_keys)
            used_mem = sum(s(vms[i].desired.memGB) * x[(i, j)] for i in vm_keys)
            used_disk = sum(s(vms[i].desired.diskGB) * x[(i, j)] for i in vm_keys)

            unused_cpu[j] = model.NewIntVar(0, s(cap.cpu), f"unused_cpu_{j}")
            unused_mem[j] = model.NewIntVar(0, s(cap.memGB), f"unused_mem_{j}")
            unused_disk[j] = model.NewIntVar(0, s(cap.diskGB), f"unused_disk_{j}")

            model.Add(unused_cpu[j] == s(cap.cpu) - used_cpu)
            model.Add(unused_mem[j] == s(cap.memGB) - used_mem)
            model.Add(unused_disk[j] == s(cap.diskGB) - used_disk)

        ########################################################################
        # max - min unused
        ########################################################################

        z_max = {}
        z_min = {}

        for j in server_keys:
            z_max[j] = model.NewIntVar(0, 10**9, f"zmax_{j}")
            z_min[j] = model.NewIntVar(0, 10**9, f"zmin_{j}")

            model.AddMaxEquality(
                z_max[j],
                [unused_cpu[j], unused_mem[j], unused_disk[j]],
            )

            model.AddMinEquality(
                z_min[j],
                [unused_cpu[j], unused_mem[j], unused_disk[j]],
            )

        ########################################################################
        # Solve
        ########################################################################

        # In order of priority, minimize
        #   rejected VMs
        #   active servers
        #   balance (max - min)
        model.Minimize(
            10_000_000 * sum(r[i] for i in vm_keys) +
            1_000_000 * sum(y[j] for j in server_keys) +
            sum(z_max[j] - z_min[j] for j in server_keys)
        )

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        solver.parameters.num_search_workers = 8

        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return []

        ########################################################################
        # Apply solution
        ########################################################################
        server_dict = {j: servers[j] for j in server_keys}

        for i in vm_keys:
            if solver.Value(r[i]) == 1:
                continue  # rejected

            for j in server_keys:
                if solver.Value(x[(i, j)]) == 1:
                    server_dict[j].schedule(vms[i])
                    break

        return []