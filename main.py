#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main script to run StateSim

# TODO: Write tests, esepecially for alliance functions -- test handling of borders if state is conquered
# TODO: Equip system with two data sets: One to monitor state level, the other system level
#       These can be converted to Pandas and exported, after end of 500 runs
# TODO: system: break network and .world into two functions, restore self.world = f() to __init__, after network initialization
# TODO: Implement stochastic economic growth

import logging
import sys
import yaml

import pandas as pd

from statesim.system import InternationalSystem
from statesim.state import State

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(levelname)s | %(asctime)s | %(name)s | %(''message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

config = yaml.full_load( open('config.yaml') )

world = InternationalSystem(config=config)

# Randomly select state
state = world.random_state()

# State looks for a target state to pick on
target = state.scan_targets()

state_est_target = state.estimate_power(target)
if state_est_target > state.power0:
    world.end_turn()#; break

# Targetted state looks for allies
# Target estimates the power of the iniating state
target_est_state = target.estimate_power(state)
if target.power0 <= target_est_state:
    target_potential_alliance = target.seek_allies(against=state)
    for ally in target_potential_alliance:
        if ally != target:
            target.propose_alliance(to=ally,
                                    alliance=target_potential_alliance,
                                    against=state)

# Re-estimate target's power; if remains less, war
# Otherwise, search for an offensive alliance
state_est_target = state.estimate_alliance(target)
if state_est_target < state.power0:
    war = world.war(state, target)
    world.assess_war_damage(war)
    world.end_turn()  # ; break
else:
    state_potential_alliance = state.seek_allies(against=target)
    for ally in state_potential_alliance:
        if ally != state:
            state.propose_alliance(to=ally,
                                   alliance=state_potential_alliance,
                                   against=target)
    # if there are any rejections, state backs down
    if len(state.alliance) < len(state_potential_alliance):
        world.end_turn()  #; break

# Target re-estimates its alliance, and state's alliance; if weaker,
# seek more allies
target_est_alliance = target.estimate_alliance(target)
target_est_state_alliance = target.estimate_alliance(state)
if target_est_alliance < target_est_state_alliance:
    target_potential_alliance = target.seek_allies(against=state)
    propose_to = [i for i in target_potential_alliance if i not in target.alliance]
    for ally in propose_to:
        target.propose_alliance(to=ally, alliance=target_potential_alliance,
                                against=state)

# State compares balance of power one last time
state_est_alliance = state.estimate_alliance(state)
state_est_target_alliance = state.estimate_alliance(target)
if state_est_alliance > state_est_target_alliance:
    war = world.war(state, target)
    world.assess_war_damage(war)

world.end_turn()


if __name__ == '__main__':

    config = yaml.full_load( open('config.yaml') )

    world = InternationalSystem(config=config)

    state_power = pd.DataFrame(columns=[0, 1, 2])

for i in range(1, 10):

    print('Iteration no. %s' % i)

    state_power = state_power.append( pd.DataFrame([(i, j.name, j.power) for j in world.world.values()]) )

    # Randomly select state
    state = world.random_state()

    # State looks for a target state to pick on
    target = state.scan_targets()

    state_est_target = state.estimate_power(target)
    if state_est_target > state.power0:
        world.end_turn()
        continue

    # Targetted state looks for allies
    # Target estimates the power of the iniating state
    target_est_state = target.estimate_power(state)
    if target.power0 <= target_est_state:
        target_potential_alliance = target.seek_allies(against=state)
        for ally in target_potential_alliance:
            if ally != target:
                target.propose_alliance(to=ally,
                                        alliance=target_potential_alliance,
                                        against=state)

    # Re-estimate target's power; if remains less, war
    # Otherwise, search for an offensive alliance
    state_est_target = state.estimate_alliance(target)
    if state_est_target < state.power0:
        war = world.war(state, target)
        world.assess_war_damage(war)
        world.end_turn()
        continue
    else:
        state_potential_alliance = state.seek_allies(against=target)
        for ally in state_potential_alliance:
            if ally != state:
                state.propose_alliance(to=ally,
                                       alliance=state_potential_alliance,
                                       against=target)
        # if there are any rejections, state backs down
        if len(state.alliance) < len(state_potential_alliance):
            world.end_turn()
            continue

    # Target re-estimates its alliance, and state's alliance; if weaker,
    # seek more allies
    target_est_alliance = target.estimate_alliance(target)
    target_est_state_alliance = target.estimate_alliance(state)
    if target_est_alliance < target_est_state_alliance:
        target_potential_alliance = target.seek_allies(against=state)
        propose_to = [i for i in target_potential_alliance if i not in target.alliance]
        for ally in propose_to:
            target.propose_alliance(to=ally, alliance=target_potential_alliance,
                                    against=state)

    # State compares balance of power one last time
    state_est_alliance = state.estimate_alliance(state)
    state_est_target_alliance = state.estimate_alliance(target)
    if state_est_alliance > state_est_target_alliance:
        war = world.war(state, target)
        world.assess_war_damage(war)

    world.end_turn()

POWER = [world.world[k].power for k in world.world.keys()]
np.mean(POWER)
#np.std(POWER)