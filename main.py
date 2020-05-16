#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main script to run StateSim

# TODO: Think about redoing main loop, make it easier to read, smaller var names
# TODO: Config logger
# TODO: Use appropriate algorithm/numpy arrays for alliance combinations
# TODO: Equip system with three data sets: One to monitor state level, the other system level
#       These can be converted to Pandas and exported, after end of 500 runs
#       One to monitor war
# TODO: system: break network and .world into two functions, restore self.world = f() to __init__, after network initialization

# Simulation control file:
#   configs = [ {}, {}, {}, ...] All configs we want
#   for config in configs:
#       ...  # run simulation
#       world.reports.state.to_csv('')
#       world.reports.system.to_csv('')
#       world.reports.war.to_csv('')

from datetime import datetime
from itertools import product
import json
import logging
import random
import sys
import yaml

import pandas as pd

from statesim.system import InternationalSystem
from statesim.sim import Simulation
from statesim.state import State

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(levelname)s | %(asctime)s | %(name)s | %(''message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

def expand_grid(dictionary):
    """ Quick function similar to expand.grid in R, used to create a
    config matrix"""
    return pd.DataFrame([row for row in product(*dictionary.values())], 
                        columns=dictionary.keys())


if __name__ == '__main__':

    # Set up matrix of config options
    config_dict = {'seed': [1804],
               'niter': [1000],
               'network_n': [98],
               'network_p': [8],
               'power_dist_mu': [10.0],
               'power_dist_sigma': [1.67, 3.33, 6.67],
               'misperception_sigma': [0.1, 0.2, 0.4],
               'victory_sigma': [1.0, 3.0, 5.0],
               'max_war_cost': [0.05, 0.1, 0.2],
               'war_cost_disp': [0.05, 0.10, 0.15],
               'reparations': [0.1, 0.2, 0.3],
               'growth_mu': [0.005, 0.01, 0.03],
               'growth_sigma': [0.01, 0.025, 0.05],
               'versailles': [True, False]}
    configs = expand_grid(config_dict)

    # Iterate over each config setting
    for config in configs.to_dict(orient='row'):

        config['seed'] = random.randint(1, 10e6)

        SIM_ID = datetime.now().strftime('%Y%m%dt%H%M%S')

        try:

            sim = Simulation(config=config)
            sim.run()

            # Save config
            config['sim_id'] = SIM_ID
            with open('./data/config/config_%s.json' % SIM_ID, 'w+') as f:
                f.write(json.dumps(config))

            # Save simulation results
            sim.state['sim_id'] = SIM_ID
            sim.system['sim_id'] = SIM_ID
            sim.wars['sim_id'] = SIM_ID

            sim.state.to_csv('./data/state/state_%s.csv' % SIM_ID, index=False)
            sim.system.to_csv('./data/system/system_%s.csv' % SIM_ID, index=False)
            sim.wars.to_csv('./data/wars/wars_%s.csv' % SIM_ID, index=False)

        except:

            # Save config as error, and resume simulation
            config['sim_id'] = SIM_ID
            with open('./data/error/config_%s.json' % SIM_ID, 'w+') as f:
                f.write(json.dumps(config))

            continue

