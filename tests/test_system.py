# python -m unittest discover -v

import unittest

from statesim.state import State
from statesim.system import InternationalSystem

config = {'seed': 1804,
          'niter': 500,
          'network_n': 98,
          'network_p': 8,
          'power_dist_mu': 10.0,
          'power_dist_sigma': 3.33,
          'misperception_sigma': 0.2,
          'victory_sigma': 1.0,
          'max_war_cost': 0.25,
          'war_cost_disp': 0.125,
          'reparations': 0.2,
          'growth_mu': 0.03,
          'growth_sigma': 0.01}

class TestSystem(unittest.TestCase):
 
    def setUp(self):
        self.world = InternationalSystem(config=config)
        self.state1 = State(name=1, power=5)
        self.state2 = State(name=2, power=7)
        self.state3 = State(name=3, power=10)

    def test_lv_1(self):
        lv = self.world.likelihood_victory(self.state2, self.state1)
        self.assertEqual(0.6829070974079555, lv)

    def test_lv_2(self):
        lv = self.world.likelihood_victory(self.state1, self.state2)
        self.assertEqual(0.3170929025920447, lv)

    def test_lv_3(self):
        self.state2.alliance.append(self.state1)
        lv = self.world.likelihood_victory(self.state3, self.state2)
        self.assertEqual(0.39826457168679225, lv)