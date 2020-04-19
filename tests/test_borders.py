# python -m unittest discover -v

import unittest

from statesim.state import State
from statesim.system import InternationalSystem


class TestBorders1(unittest.TestCase):
    """ State 1 conquers State 2 on a network n=5, p=2."""
 
    def setUp(self):

        config = {'seed': 1804,
          'niter': 500,
          'network_n': 5,
          'network_p': 2,
          'power_dist_mu': 10.0,
          'power_dist_sigma': 3.33,
          'misperception_sigma': 0.2,
          'victory_sigma': 1.0,
          'max_war_cost': 0.25,
          'war_cost_disp': 0.125,
          'reparations': 0.2,
          'growth_mu': 0.03,
          'growth_sigma': 0.01,
          'versailles': True}

        self.world = InternationalSystem(config=config)
        self.world.world[0].border = [self.world.world[3], self.world.world[4]]
        self.world.world[1].border = [self.world.world[2], self.world.world[4]]
        self.world.world[2].border = [self.world.world[1], self.world.world[3]]
        self.world.world[3].border = [self.world.world[0], self.world.world[2]]
        self.world.world[4].border = [self.world.world[0], self.world.world[1]]

        self.world.world[1].power = 40
        self.world.world[2].power = 1

    def test_borders1(self):
        
        a = self.world.world[1]
        b = self.world.world[2]
        war = self.world.war(a, b)
        self.world.assess_war_damage(war)
        self.world.end_turn()

        # Sort so they match up
        self.world.world[1].border.sort()
        border_test = [self.world.world[3], self.world.world[4]]
        border_test.sort()

        # 1 conquers 2, so 1 border: 3, 4
        self.assertEqual(self.world.world[1].border, border_test)



class TestBorders2(unittest.TestCase):
    """ Sets up a larger network, with n=6 and p=3. First tests tests State 1
    conquering state 2.

    Second test repeats this, then has State 1 conquer State 3."""
 
    def setUp(self):

        config = {'seed': 1804,
          'niter': 500,
          'network_n': 6,
          'network_p': 3,
          'power_dist_mu': 10.0,
          'power_dist_sigma': 3.33,
          'misperception_sigma': 0.2,
          'victory_sigma': 1.0,
          'max_war_cost': 0.25,
          'war_cost_disp': 0.125,
          'reparations': 0.2,
          'growth_mu': 0.03,
          'growth_sigma': 0.01,
          'versailles': True}

        self.world = InternationalSystem(config=config)
        self.world.world[0].border = [self.world.world[1], self.world.world[4], self.world.world[3]]
        self.world.world[1].border = [self.world.world[0], self.world.world[2], self.world.world[5]]
        self.world.world[2].border = [self.world.world[1], self.world.world[3], self.world.world[5]]
        self.world.world[3].border = [self.world.world[2], self.world.world[4], self.world.world[0]]
        self.world.world[4].border = [self.world.world[5], self.world.world[0], self.world.world[3]]
        self.world.world[5].border = [self.world.world[4], self.world.world[1], self.world.world[2]]

        self.world.world[1].power = 40
        self.world.world[2].power = 1
        self.world.world[3].power = 1

    def test_borders2_1(self):
        
        a = self.world.world[1]
        b = self.world.world[2]
        war = self.world.war(a, b)
        self.world.assess_war_damage(war)
        self.world.end_turn()

        # Sort so they match up
        self.world.world[1].border.sort()
        border_test = [self.world.world[0], self.world.world[3], self.world.world[5]]
        border_test.sort()

        # 1 conquers 2, so 1 border: 3, 4
        self.assertEqual(self.world.world[1].border, border_test)

    def test_borders2_2(self):
        """ Two stage test: First, State 1 conquers state 2. Second, State 1
        conquers State 3."""

        # First part
        a = self.world.world[1]
        b = self.world.world[2]
        war = self.world.war(a, b)
        self.world.assess_war_damage(war)
        self.world.end_turn()

        # Sort so they match up
        self.world.world[1].border.sort()
        border_test = [self.world.world[0], self.world.world[3], self.world.world[5]]
        border_test.sort()

        # Second part        
        a = self.world.world[1]
        b = self.world.world[3]
        war = self.world.war(a, b)
        self.world.assess_war_damage(war)
        self.world.end_turn()

        self.world.world[1].border.sort()
        border_test = [self.world.world[0], self.world.world[4], self.world.world[5]]
        border_test.sort()

        self.assertEqual(self.world.world[1].border, border_test)
        