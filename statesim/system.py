#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate as integrate
from scipy.stats import cauchy

from statesim.state import State

logger = logging.getLogger(__name__)


class InternationalSystem(object):
    """ Main object controlling the simulation.

    Attributes
    ----------
    config : dict
        houses parameters governing the simulation

    Methods
    -------
    generate_world()
        Generates a dict of State objects and their borders and diplomacy
    random_power()
        Used to randomly assign initial power levels to states
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config : dict
            houses parameters governing the simulation
        """
        self.config = config
        self.turn = 0
        self.state = []
        self.system = []
        self.wars = []
        self.network = self.generate_world()
        
        self.draw_borders(self.network)

    def generate_world(self):
        """ Creates the world. First, uses networkx to generate a 'map' which
        is represented by a network with each node as a state, and each edge as
        a border.

        The network is converted to a dictionary.

        The initial power distribution is calculated and assigned to each state.
        """

        network = nx.random_regular_graph(self.config['network_p'],
                                          self.config['network_n'],
                                          seed=self.config['seed'])

        # Initialize all states
        world = {}
        for i in network.nodes:
            state = State(name=i, power=self.random_power(),
                          misperception=self.config['misperception_sigma'])
            world[i] = state

        self.world = world

        # Record initial distribution of power
        power_dist = np.array([i.power for i in world.values()])
        first_turn = {'turn': 0,
                      'n': len(world),
                      'min': np.min(power_dist),
                      'p25': np.percentile(power_dist, 0.25),
                      'p50': np.percentile(power_dist, 0.5),
                      'p75': np.percentile(power_dist, 0.75),
                      'max': np.max(power_dist),
                      'avg': np.mean(power_dist),
                      'sd': np.std(power_dist)}
        self.system.append(first_turn)

        return network

    def draw(self):
        """
        """
        nx.draw_networkx(self.network)

    def draw_borders(self, network):
        """ """
        # Wipe out existing borders
        for i in self.world.keys():
            try:
                neighbors = [j for j in self.network.neighbors(i) if j != i]
                self.world[i].border = [self.world[j] for j in neighbors]
            except KeyError:
                raise

    def likelihood_victory(self, a, b):
        """ Returns the probability state A wins a war against state B.

        Computes the area underneath a logistic function between the log of
        the power ratio of the two states.

        The parameter victory_sigma controls how 'steep' the curve is. As
        sigma increases, chance becomes more important; less powerful states
        have a greater chance of victory against more pwoerful states. The
        power ratio becomes more and more deterministic and sigma decreases.
        """
        a_power = sum(a.alliance)
        b_power = sum(b.alliance)
        sigma = self.config['victory_sigma']
        const = 1 / np.sqrt(np.pi * sigma)
        f = lambda x: np.exp( -1 * np.square(x / sigma) )
        area = integrate.quad( f, -np.inf, np.log(a_power / b_power) )
        lv_init = area[0] * const
        if lv_init < 0:
            lv = 0.0
        elif lv_init > 1:
            lv = 1.0
        else:
            lv = lv_init
        return lv

    def record_peace(self, a, b):
        """ Records outcomes where no war occurs to war data set.
        """
        peace = {'turn': self.turn,
                 'war': False,
                 'offense': a.name,
                 'defense': b.name,
                 'offense0': a.power,
                 'defense0': b.power,
                 'offense1': sum([i.power for i in a.alliance]),
                 'defense1': sum([i.power for i in b.alliance]),
                 'outcome': 'NA'}

        self.wars.append(peace)

        return None

    def war(self, a, b):
        """ Determines which side wins the war. Returns object specifying data,
        about the war, which is then used to determine war costs, etc.

        Calculates the probility a beats b, using a logistic function. Then
        uses this probability as p in a single binomial trial. If result is 1,
        a wins; else b wins.

        Returns
        """
        lv = self.likelihood_victory(a, b)
        victory = bool( np.random.binomial(1, lv, 1) )

        war = {'turn': self.turn,
               'war': True,
               'offense': a.name,
               'defense': b.name,
               'offense0': a.power,
               'defense0': b.power,
               'offense1': sum([i.power for i in a.alliance]),
               'defense1': sum([i.power for i in b.alliance]),
               'outcome': a.name if victory == True else b.name}
        self.wars.append(war)

        return {'victor': a if victory == True else b,
                'loser': b if victory == True else a,
                'offense': a,
                'defense': b,
                'likelihood_victory': lv,
                'lsr': max(a.power, b.power) / (a.power + b.power)}

    def assess_war_damage(self, war):
        """
        Imposes a war cost equally to all sides. The parameter max_war_cost
        controls how costly this can be. By default, since max_war_cost is .25,
        no state can lose more than 25 percent of their power in a war. The war
        war cost percentage is applied equally to all victor and loser states
        and their allies.

        2. Take reparations form losing side and distribute to winning side
        """
        # War cost
        max_cost = self.config['max_war_cost']
        lsr = war['lsr']
        war_cost = (1.0 - ((lsr - 0.5) / 0.5)) * max_cost
        weight = min(self.config['war_cost_disp'], max_cost * np.random.uniform())

        victor_states = war['victor'].alliance
        loser_states = war['loser'].alliance

        #################
        # Versailles rule

        if self.config['versailles']:

            # if state is victor:
            if war['victor'] == war['offense']:
            # target surrenders LV% of power
                transfer = war['loser'].power * war['likelihood_victory']
                war['loser'].power = war['loser'].power - transfer
                war['victor'].power += transfer
            # elif target is victor:
            elif war['victor'] == war['defense']:
            # state surrenders 1-LV % of power
                transfer = war['victor'].power * (1 - war['likelihood_victory'])
                war['victor'].power = war['victor'].power - transfer
                war['loser'].power += transfer

        #################

        for i in victor_states:
            cost = max(war_cost - weight, 0.01)
            i.power = max(i.power * (1 - cost), 1)  # do not let victors fall below 1
            logger.info('%s assessed war damage of %s percent' % (i, round(cost, 2)*100))

        for i in loser_states:
            cost = min(1, war_cost + weight)
            i.power = i.power * (1 - cost)
            logger.info('%s assessed war damage of %s percent' % (i, round(cost, 2)*100))

        # Spoils -- TODO seperate function
        total_reparations = sum( [i.power * self.config['reparations'] for i in loser_states] )
        for i in loser_states:
            reparations = max(i.power * self.config['reparations'], .01)
            i.power = i.power - reparations
            logger.info('%s is forced to pay %s power units in reparations' % (i, round(reparations, 2)))

        # Each victor recieves a portion of spoils, proportionate to their
        # contribution to total power of alliance
        total_victor_power = sum(victor_states)
        for i in victor_states:
            reparations = total_reparations * (i.power / total_victor_power)
            i.power += reparations
            logger.info('%s has claimed %s power units as spoils of war' % (i, round(reparations, 2)))

        for k in self.world.keys():
            if self.world[k].power < 1.0:
                self.world[k].conquered = war['victor']


    def end_turn(self):
        """ 1. Remove states with no power left; if so, redraw network and borders
        2. Wipe out alliances
        3. Economic growth

        Power adjustment segment. A. Eliminate all states with no remaining 
        power or cells of territory. B. End the run if only one state is left 
        or the iteration limit is reached. Otherwise, grant all remaining states
         internal power growth of 3 percent. The simulation moves to segment.
        """
        for k in list(self.world.keys()):
            if self.world[k].power < 1:
                logger.info('State %s is removed from system' % k)

                # Record state death
                # STATE: state ID | turn death |
                death = {'state_id': k,
                         'survived_to': self.turn}
                self.state.append(death)

                # If conquered, give borders to conquering state and delete from system
                n = k
                neighbors = [j for j in self.network.neighbors(n) if self.world[j].power > 1]
                new_borders = [j for j in neighbors if j != k and self.world[j].power > 1]
                for j in new_borders:
                    self.network.add_edge(self.world[k].conquered.name, j)
                self.network.remove_node(k)
                del self.world[k]
            else:
                self.world[k].alliance = [self.world[k]]
                # growth = np.random.normal(loc=self.config['growth_mu'],
                #                           scale=self.config['growth_sigma'])
                growth = self.random_growth()
                self.world[k].power = max(self.world[k].power * (1 + growth), 1)  # cannot grow below 0

                # Update power0 assessments of themselves
                power = self.world[k].power
                power0 = power * np.random.normal(loc=1, scale=self.config['misperception_sigma'])
                self.world[k].power0 = power0

        self.draw_borders(self.network)

        # Record distribution of power
        power_dist = np.array([i.power for i in self.world.values()])
        power_record = {'turn': self.turn,
                        'n': len(self.world),
                        'min': np.min(power_dist),
                        'p25': np.percentile(power_dist, 0.25),
                        'p50': np.percentile(power_dist, 0.5),
                        'p75': np.percentile(power_dist, 0.75),
                        'max': np.max(power_dist),
                        'avg': np.mean(power_dist),
                        'sd': np.std(power_dist)}
        self.system.append(power_record)

        logger.info('Turn ended')

    def random_growth(self):
        """ Cauchy distribution with barriers at -30 and 15 percent.
        """
        growth = cauchy.rvs(size=1, loc=self.config['growth_mu'],
                            scale=self.config['growth_sigma'])[0]
        if growth < -0.30:
            return -0.30
        elif growth > 0.15:
            return 0.15
        else:
            return growth

                         

    def random_power(self):
        """ Used to assign a random power level to a state in the
        initialization phase.

        Generates a random number from a normal distribution with a mean and
        standard deviation specified in the config file. Does not permit power
        to fall below one.
        """
        power_init = np.random.normal(loc=self.config['power_dist_mu'],
                                      scale=self.config['power_dist_sigma'])
        power = max(power_init, 1)
        return power

    def plot_power(self):
        """
        """
        x = [self.world[k].power for k in self.world.keys()]
        plt.hist(x)

    def random_state(self):
        """ Returns a random state from the world, propotional to its share
        of power in the world.
        """
        states = [k for k in self.world.keys()]
        total_power = sum([self.world[i].power for i in states])
        power_dist = [self.world[i].power / total_power for i in states]
        random_state = np.random.choice(states, 1, power_dist)[0]

        return self.world[random_state]
