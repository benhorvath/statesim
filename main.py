#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Main script to run StateSim

# TODO: system.plot_power(): Plots histogram of distribution of power of states!
# TODO: Write tests, esepecially for alliance functions
# TODO: Sketch out entire flow of main.__main__() and make it iterable
# TODO: Equip system with two data sets: One to monitor state level, the other system level
#       These can be converted to Pandas and exported, after end of 500 runs
# TODO: test handling of borders if state is conquered
# TODO: system: break network and .world into two functions, restore self.world = f() to __init__, after network initialization
# TODO: war damage can never be less than 0!
# TODO: States when initialized estimate their own power
# TODO: Make sure everyone is using skewed estimates of their own power

import logging
import sys
import yaml

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

if state_est_target > state.power:
    world.end_turn()#; break

# Targetted state looks for allies
# Target estimates the power of the iniating state
target_est_state = target.estimate_power(state)
if target.power <= target_est_state:
    target_potential_alliance = target.seek_allies(against=state)
    # TODO: Fix this, also does not have self in .alliance !
    for ally in target_potential_alliance:
        if ally != target:
            target.propose_alliance(to=ally,
                                    alliance=target_potential_alliance,
                                    against=state)

# Initiator's rejoinder to target's diplomacy
# IF target fails to get alliances, go for war:
state_est_target_alliance = state.estimate_alliance(target)
if len(target.alliance) == 1:
    war = world.war(state, target)
# initiator compares power with target coalition's allinace's power
elif state.power > state_est_target_alliance:
    war = world.war(state, target)
else:
    state_potential_alliance = state.seek_allies(against=target)
    for ally in state_potential_alliance[1:]:
        state.propose_alliance(to=ally, alliance=state_potential_alliance,
                               against=target)
    # if such a coalition was needed and does not exist, end conflict and break
    if len(state.alliance) == 1:
        world.end_turn() # ; break
    # if all states poposed to join, then continue to war; else back down
    elif len(state.alliance) < len(state_potential_alliance):
        world.end_turn()# ; break

# Target gets one last chance for allies and diplomacy
# If target+alliance has more powerful, do nothing
# if target+alliance is not as powerful, more alliance building
target_est_alliance = target.estimate_alliance(target)
target_est_state_alliance = target.estimate_alliance(state)
if target_est_alliance < target_est_state_alliance:
    target_potential_alliance = target.seek_allies(against=state)
    target_potential_alliance = [i for i in target_potential_alliance if i not in target.alliance]
    for ally in target_potential_alliance:
        target.propose_alliance(to=ally, alliance=target_potential_alliance,
                                against=state)

# State compares its forces to alliance one last time
state_est_target_alliance = state.estimate_alliance(target)
if sum(state.alliance) > state_est_target_alliance:
    war = world.war(state, target)
    world.assess_war_damage(war)

world.end_turn()



if __name__ == '__main__':

    config = yaml.full_load( open('config.yaml') )

    world = InternationalSystem(config=config)

    for i in range(1, config.niter):

        print('Iteration no. %s' % i)

        # Randomly select state
        state = world.random_state()

        # State looks for a target state to pick on
        target = state.scan_targets()

        # Targetted state looks for allies
        if target.power <= state.power:
            target_potential_allies = target.seek_allies()
            world.offer_alliance(originator=target,
                                 recipients=target_potential_allies)

        # Original, initiating state looks for allies
        if state.power < sum( [i.power for i in target.allies] ):
            state_potential_allies = state.seek_allies()
            world.offer_alliance(originator=state,
                                 recipients=state_potential_allies)

        # Calculate final balance of power, war or peace ensues
        if sum( [i.power for i in state.allies] ) > sum( [i.power for i in target.allies] ):
            # War!
            war = world.war(state, target)
            world.assess_war_damage(war)

        world.end_turn()