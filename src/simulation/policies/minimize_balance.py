from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM
import pulp

class MinimizeBalance(SchedulingPolicy):
    def place(self, vms: list[VM], servers: list[Server]):
        server_dict: dict[str, Server] = {}
        for server in servers:
            server_dict[str(server)] = server
        server_keys = list(server_dict.keys())

        vm_dict: dict[str, VM] = {}
        for vm in vms:
            vm_dict[str(vm)] = vm
        vm_keys = list(vm_dict.keys())

        model = pulp.LpProblem("Minimize_Balance", pulp.LpMinimize)

        ########################################################################
        # Decision variables
        ########################################################################

        # x[i][j] = 1 if VM i is assigned to server j
        x = pulp.LpVariable.dicts("x", (vm_keys, server_keys), cat="Binary")

        # y[j] = 1 if server j is active
        y = pulp.LpVariable.dicts("y", server_keys, cat="Binary")

        ########################################################################
        # Constraints
        ########################################################################

        # Each VM is assigned to exactly one server
        for i in vm_keys:
            model += pulp.lpSum(x[i][j] for j in server_keys) == 1

        # Server capacity constraints
        for j in server_keys:
            capacity = server_dict[j].capacity

            model += pulp.lpSum(vm_dict[i].desired.cpu * x[i][j] for i in vm_keys) <= capacity.cpu * y[j]
            model += pulp.lpSum(vm_dict[i].desired.memGB  * x[i][j] for i in vm_keys) <= capacity.memGB * y[j]
            model += pulp.lpSum(vm_dict[i].desired.diskGB  * x[i][j] for i in vm_keys) <= capacity.diskGB * y[j]

        ########################################################################
        # Helper variables for balance
        ########################################################################

        z_max = pulp.LpVariable.dicts('z_max', server_keys, lowBound=0)
        z_min = pulp.LpVariable.dicts('z_min', server_keys, lowBound=0)

        for sk in server_keys:
            server = server_dict[sk]

            u_cpu = server.capacity.cpu - pulp.lpSum(x[vk][sk] * vm_dict[vk].desired.cpu for vk in vm_keys)
            r_cpu = u_cpu / server.capacity.cpu

            model += z_max[sk] >= r_cpu
            model += z_min[sk] <= r_cpu

            u_mem = server.capacity.memGB - pulp.lpSum(x[vk][sk] * vm_dict[vk].desired.memGB for vk in vm_keys)
            r_mem = u_mem / server.capacity.memGB

            model += z_max[sk] >= r_mem
            model += z_min[sk] <= r_mem

            u_disk = server.capacity.diskGB - pulp.lpSum(x[vk][sk] * vm_dict[vk].desired.diskGB for vk in vm_keys)
            r_disk = u_disk / server.capacity.diskGB
            
            model += z_max[sk] >= r_disk
            model += z_min[sk] <= r_disk

        ########################################################################
        # Objective function
        ########################################################################

        model += (
            # Heavily weigh active servers to simulate lexographic priority
            10_000 * pulp.lpSum(y[j] for j in server_keys) +
            pulp.lpSum((z_max[j] - z_min[j]) for j in server_keys)
        )

        ########################################################################
        # Solve the model
        ########################################################################

        model.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))

        for i in vm_keys: 
            for j in server_keys:
                if pulp.value(x[i][j]) == 1:
                    if server_dict[j].hasSpaceFor(vm_dict[i]):
                        server_dict[j].schedule(vm_dict[i])
                        break

