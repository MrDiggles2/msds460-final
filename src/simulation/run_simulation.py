from simulation.core.fleet import Fleet
from simulation.core.resource_set import ResourceSet
from simulation.simulation import Simulation
from simulation.policies.first_fit import FirstFitPolicy
from simulation.policies.minimize_active_servers import MinimizeActiveServers
from simulation.policies.min_active_min_strand import MinActiveMinStrand

import argparse
import time
import logging
import pandas as pd
import numpy as np

POLICY_MAP = {
    "first_fit": FirstFitPolicy,
    "min": MinimizeActiveServers,
    'min2':  MinActiveMinStrand,
}

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-n",
        type=int,
        default=1,
        help="Number of simulation runs"
    )

    parser.add_argument(
        "--vm-count",
        type=int,
        default=10,
        help="Number of VM requests"
    )

    parser.add_argument(
        "--server-count",
        type=int,
        default=1,
        help="Number of servers"
    )

    parser.add_argument(
        "--policy",
        type=str,
        default="first_fit",
        choices=POLICY_MAP.keys(),
        help="Scheduling policy to use"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )

    return parser.parse_args()

def main():
    args = parse_args()

    logging.basicConfig(level = 'DEBUG' if args.verbose else 'INFO')
    policy = POLICY_MAP[args.policy]()

    results = []

    for i in range(args.n):

        if not args.verbose:
            print('.', end='', flush=True) # so we can get a sense of progress

        fleet = Fleet(args.server_count, ResourceSet(cpu = 96, memGB = 256, diskGB = 1024))
        simulation = Simulation(fleet, args.vm_count, policy)

        simulation.run()

        scheduled_count = sum(len(s.scheduledVMs) for s in simulation.fleet.servers)
        rejected_count = args.vm_count - scheduled_count

        result = {
            "scheduled_count": scheduled_count,
            "rejected_count": rejected_count,
        }

        logging.debug('-' * 80)
        logging.debug(f'SIM #{i} | scheduled={scheduled_count} rejected={rejected_count}')

        for server_idx, server in enumerate(simulation.fleet.servers):

            remaining = server.getAvailableCapacity()
            capacity = server.capacity

            cpu_util = 1 - remaining.cpu / capacity.cpu
            mem_util = 1 - remaining.memGB / capacity.memGB
            disk_util = 1 - remaining.diskGB / capacity.diskGB

            balance = max(cpu_util, mem_util, disk_util) - min(
                cpu_util, mem_util, disk_util
            )

            result[f"server_{server_idx}_cpu_util"] = cpu_util
            result[f"server_{server_idx}_mem_util"] = mem_util
            result[f"server_{server_idx}_disk_util"] = disk_util
            result[f"server_{server_idx}_balance"] = balance

            logging.debug(
                f"\t{server.id}"
                f" | vms={len(server.scheduledVMs)}"
                f" | cpu={cpu_util:.2%}"
                f" | mem={mem_util:.2%}"
                f" | disk={disk_util:.2%}"
                f" | balance={balance:.3f}"
            )

        results.append(result)

    if not args.verbose:
        print('')
    logging.debug('-' * 80)

    df = pd.DataFrame(results)

    print(f"\nSimulation completed over n={args.n} runs")

    def mean_ci(series):
        mean = series.mean()
        se = series.std(ddof=1) / np.sqrt(len(series))
        margin = 1.96 * se
        return mean, mean - margin, mean + margin

    print("\n=== VM Placement Summary ===\n")

    for metric in ["scheduled_count", "rejected_count"]:
        mean, lower, upper = mean_ci(df[metric])

        print(
            f"{metric:<20}"
            f"{mean:>10.2f}"
            f" [{lower:.2f}, {upper:.2f}]"
        )

    print("\n=== Average Server Utilization ===\n")

    for server_idx in range(args.server_count):

        cpu_mean = df[f"server_{server_idx}_cpu_util"].mean()
        mem_mean = df[f"server_{server_idx}_mem_util"].mean()
        disk_mean = df[f"server_{server_idx}_disk_util"].mean()

        print(
            f"Server {server_idx:<2}"
            f" CPU={cpu_mean:6.1%}"
            f" MEM={mem_mean:6.1%}"
            f" DISK={disk_mean:6.1%}"
        )

    print("\n=== Average Server Balance ===\n")

    for server_idx in range(args.server_count):

        mean, lower, upper = mean_ci(
            df[f"server_{server_idx}_balance"]
        )

        print(
            f"Server {server_idx:<2}"
            f" balance={mean:.3f}"
            f" [{lower:.3f}, {upper:.3f}]"
        )

    filename = f'./output/results-{time.time()}.csv'
    print(f"\nFull results written to {filename}\n")
    df.to_csv(filename)