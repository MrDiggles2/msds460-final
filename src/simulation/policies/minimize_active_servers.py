from simulation.policies.base import SchedulingPolicy
from simulation.core.server import Server
from simulation.core.vm import VM
import pulp

class MinimizeActiveServers(SchedulingPolicy):
    def place(self, vms: list[VM], servers: list[Server]):
        server_dict: dict[str, Server] = {}
        for server in servers:
            server_dict[str(server)] = server
        server_keys = list(server_dict.keys())

        vm_dict: dict[str, VM] = {}
        for vm in vms:
            vm_dict[str(vm)] = vm
        vm_keys = list(vm_dict.keys())

        ########################################################################
        # Decision variables
        ########################################################################

        # x[i][j] = 1 if VM i is assigned to server j
        x = pulp.LpVariable.dicts("x", (vm_keys, server_keys), cat="Binary")

        # y[j] = 1 if server j is active
        y = pulp.LpVariable.dicts("y", server_keys, cat="Binary")

        ########################################################################
        # Model and objective function
        ########################################################################

        model = pulp.LpProblem("Minimize_Active_Servers", pulp.LpMinimize)
        model += pulp.lpSum(y[j] for j in server_keys)

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
        # Solve the model
        ########################################################################

        model.solve(pulp.PULP_CBC_CMD(msg=False))

        for i in x: 
            for j in y:
                if pulp.value(x[i][j]) == 1:
                    if server_dict[j].hasSpaceFor(vm_dict[i]):
                        server_dict[j].schedule(vm_dict[i])
                        break

