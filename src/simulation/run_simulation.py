from simulation.core.fleet import Fleet
from simulation.core.resource_set import ResourceSet
from simulation.simulation import Simulation
from simulation.policies.first_fit import FirstFitPolicy
from simulation.policies.goal_programming import GoalProgrammingPolicy

import argparse
import time
import logging
import pandas as pd

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
        type=bool,
        default=False
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

        logging.debug('--------------------------------------------------------------------------------')
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
    logging.debug('--------------------------------------------------------------------------------')

    df = pd.DataFrame(results)
    filename = f'output/naive-{int(time.time())}.csv'
    df.to_csv(filename)
    logging.info(f'Wrote simulation results to {filename}')
