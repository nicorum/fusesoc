#!/usr/bin/python
import argparse

from orpsoc.build import BackendFactory
from orpsoc.config import Config
from orpsoc.simulator import SimulatorFactory
from orpsoc.system import System
from orpsoc.core import Core
import os

def build(args):
    system_file = Config().get_systems()[args.system]
    system = System(system_file)

    backend = BackendFactory(system)
    backend.configure()
    backend.build()
    
def list_cores(known, remaining):
    cores = Config().get_cores()
    print("Available cores:")
    maxlen = max(map(len,cores))
    print('Core'.ljust(maxlen) + '   Cache status')
    print("="*80)
    for core_name in cores:
        try:
            core = Core(cores[core_name])
        except SyntaxError as e:
            print(core_name.ljust(maxlen) + ' : Error! ' + str(e))
            core = None
        if core:
            print(core_name.ljust(maxlen) + ' : ' + core.cache_status())

def list_systems(known, remaining):
    print("Available systems:")
    for system in Config().get_systems():
        print(system)

def sim(known, remaining):
    system_file = Config().get_systems()[known.system]
    system = System(system_file)
    
    if known.sim:
        sim_name = known.sim[0]
    elif system.simulators:
        sim_name = system.simulators[0]
    else:
        print("No simulator was found in "+ known.system + " system description")
        exit(1)
    sim = SimulatorFactory(sim_name, system)
    sim.configure()
    sim.build()
    if not known.build_only:
        sim.run(remaining)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    #General options
    parser_build = subparsers.add_parser('build', help='Build an FPGA load module')
    parser_build.add_argument('system')
    parser_build.set_defaults(func=build)

    parser_list_systems = subparsers.add_parser('list-systems', help='List available systems')
    parser_list_systems.set_defaults(func=list_systems)

    parser_list_cores = subparsers.add_parser('list-cores', help='List available cores')
    #parser_list_cores.
    parser_list_cores.set_defaults(func=list_cores)

    #Simulation subparser
    parser_sim = subparsers.add_parser('sim', help='Setup and run a simulation')
    parser_sim.add_argument('--sim', nargs=1, help='Override the simulator settings from the system file')
    parser_sim.add_argument('--build-only', action='store_true', help='Build the simulation binary without running the simulator')
    parser_sim.add_argument('--dry-run', action='store_true')
    parser_sim.add_argument('system',help='Select a system to simulate', choices = Config().get_systems())
    parser_sim.set_defaults(func=sim)

    known, remaining = parser.parse_known_args()

    known.func(known, remaining)
