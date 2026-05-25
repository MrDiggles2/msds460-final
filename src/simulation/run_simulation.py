from simulation.core.fleet import Fleet
from simulation.core.resource_set import ResourceSet
from simulation.simulation import Simulation
from simulation.policies.first_fit import FirstFitPolicy
from simulation.policies.goal_programming import GoalProgrammingPolicy

import argparse
import time
import logging
import pandas as pd
import numpy as np

POLICY_MAP = {
    "first_fit": FirstFitPolicy,
    "goal": GoalProgrammingPolicy
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

        result = simulation.run()

        scheduled_count = sum(len(s.scheduledVMs) for s in simulation.fleet.servers)
        rejected_count = args.vm_count - scheduled_count

        logging.debug('-' * 80)
        logging.debug(f'SIM #{i} | scheduled={scheduled_count} rejected={rejected_count}')
        logging.debug(f'stranded: {result.totalStranded}')
        logging.debug(f'unused: {result.totalUnused}')
        for server in simulation.fleet.servers:
            logging.debug(f'\t{server.id} | vms={len(server.scheduledVMs)} | remaining={server.getAvailableCapacity()}')

        results.append({
            "scheduled_count": scheduled_count,
            "rejected_count": rejected_count,
            "unused_cpu": result.totalUnused.cpu,
            "unused_memGB": result.totalUnused.memGB,
            "unused_diskGB": result.totalUnused.diskGB,
            "stranded_cpu": result.totalStranded.cpu,
            "stranded_memGB": result.totalStranded.memGB,
            "stranded_diskGB": result.totalStranded.diskGB,
        })

    if not args.verbose:
        print('')
    logging.debug('-' * 80)

    df = pd.DataFrame(results)

    print(f"\nSimulation completed over n={args.n} runs")
    metrics = {
        "scheduled_count": df["scheduled_count"],
        "unused_cpu": df["unused_cpu"],
        "unused_memGB": df["unused_memGB"],
        "unused_diskGB": df["unused_diskGB"],
    }

    print("\n---------------------- Summary Statistics (mean ± 95% CI) ----------------------")

    for name, series in metrics.items():
        mean, lower, upper = mean_ci(series)
        print(f"{name:<18} {mean:>10.3f} {lower:>12.3f} {upper:>12.3f}")

    print('-' * 80)
    filename = f'output/sim-results-{int(time.time())}.csv'
    df.to_csv(filename)
    print(f'\nWrote full simulation results to {filename}\n')

def mean_ci(series, confidence=1.96):
    mean = series.mean()
    std_err = series.std(ddof=1) / np.sqrt(len(series))
    lower = mean - confidence * std_err
    upper = mean + confidence * std_err
    return mean, lower, upper