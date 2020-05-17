#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import pandas as pd

from statesim.system import InternationalSystem
from statesim.state import State

logger = logging.getLogger(__name__)

class Simulation(object):
    """ Main object controlling the simulation.
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config : dict
            houses parameters governing the simulation
        """
        self.config = config
        self.state = None
        self.system = None
        self.war = None
        self.world = None

    def run(self):

        world = InternationalSystem(config=self.config)

        self.world = world
        
        # WRITE SYSTEM: self.generate_world(): initial power distribution

        for i in range(1, self.config['niter']):

            world.turn = i

            if len(world.world) == 1:
                print('Universal empire')
                break
        
            # Randomly select state
            state = world.random_state()

            # State looks for a target state to pick on; if none are weaker, go to 
            # next turn
            target = state.scan_targets()
            if target is None:
                continue

            state_est_target = state.estimate_power(target)
            if state_est_target > state.power0:
                world.record_peace(state, target)
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
                    world.record_peace(state, target)
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
            else:
                world.record_peace(state, target)

            world.end_turn()

        # Write data back to Simulation object
        self.wars = pd.DataFrame(world.wars)
        self.system = pd.DataFrame(world.system)
        self.state = pd.DataFrame(world.state)