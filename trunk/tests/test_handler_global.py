import unittest

from test import TestbedServer


class TestHandlerGlobal(unittest.TestCase):
    def setUp(self):
        self.server = TestbedServer()

        self.sock1 = self.server.connection(1)
        self.p1 = self.server.map_login('Fritz')
        if not self.p1:
            self.sock1.sendlines('Fritz', 'password')
            self.p1 = self.server.map_login('Fritz')
            if not self.p1:
                self.sock1.sendlines('new', 'Fritz', 'password', '1', '2')
                self.p1 = self.server.map_login('Fritz')

    def test_time(self):
        self.sock1.sendline('time')
        self.assertIn('since the', self.sock1.script)

    def test_stats_01_list_unallocated(self):
        self.sock1.sendline('stats')
        self.assertIn('Strength: ', self.sock1.script)
        self.assertIn('not yet allocated', self.sock1.script)

    def test_stats_02_allocate_01_0args(self):
        self.sock1.sendline('alloc')
        self.assertIn(' which stat?', self.sock1.script)

    def test_stats_02_allocate_02_1arg_invalid(self):
        self.sock1.sendline('alloc cookies')
        self.assertIn('valid stat', self.sock1.script)

    def test_stats_02_allocate_03_1arg_valid(self):
        self.sock1.sendline('alloc str')
        self.assertIn('has been increased by 1', self.sock1.script)
        self.assertEqual(self.p1.stats['strength'], 4)

    def test_stats_02_allocate_04_3args_hirange(self):
        self.sock1.sendline('alloc int 10')
        self.assertIn('that many points', self.sock1.script)

    def test_stats_02_allocate_05_3args_invalid(self):
        self.sock1.sendline('alloc cookies 2')
        self.assertIn('valid stat', self.sock1.script)

    def test_stats_02_allocate_06_3args_negative(self):
        self.sock1.sendline('alloc int -1')
        self.assertIn('that many points', self.sock1.script)

    def test_stats_02_allocate_07_3args_text(self):
        self.sock1.sendline('alloc int lots')
        self.assertIn('Please input a number', self.sock1.script)

    def test_stats_02_allocate_08_3args_sufficient(self):
        self.sock1.sendline('alloc agility 4')
        self.assertIn('has been increased by 4', self.sock1.script)
        self.assertEqual(self.p1.stats['agility'], 7)

    def test_stats_02_allocate_09_4args(self):
        self.sock1.sendline('alloc agility 4 5')
        self.assertIn('was not understood', self.sock1.script)

    def test_stats_03_list_allocated(self):
        self.sock1.sendline('stats')
        self.assertNotIn('not yet allocated', self.sock1.script)

    def test_hp(self):
        self.sock1.sendline('hp')
        self.assertIn('HP: ', self.sock1.script)

    def test_stance_01_list(self):
        self.sock1.sendline('stance')
        self.assertIn('STANCES:', self.sock1.script)

    def test_stance_02_gm_insert(self):
        self.sock1.sendline('gm getstance jiujitsu')
        self.sock1.sendline('gm getstance lancer')
        self.sock1.sendline('stance')
        self.assertIn('STANCES:', self.sock1.script)
        self.assertIn('Brawling*+', self.sock1.script)
        self.assertIn('Jiujitsu', self.sock1.script)
        self.assertIn('Lancer', self.sock1.script)

    def test_stance_03_usage(self):
        self.sock1.sendline('stance help')
        self.assertIn('STANCE USAGE', self.sock1.script)

    def test_stance_03_usage_short(self):
        self.sock1.sendline('stance h')
        self.assertIn('STANCE USAGE', self.sock1.script)

    def test_stance_04_invalid_toplevel(self):
        self.sock1.sendline('stance x')
        self.assertIn('That is not a valid usage for STANCE.', self.sock1.script)

    def test_stance_05_default(self):
        self.sock1.sendline('stance default')
        self.assertIn('want as your default?', self.sock1.script)

    def test_stance_05_default_short(self):
        self.sock1.sendline('stance d')
        self.assertIn('want as your default?', self.sock1.script)

    def test_stance_05_default_set_invalid(self):
        self.sock1.sendline('stance default crawling')
        self.assertIn("don't have a stance like that", self.sock1.script)

    def test_stance_05_default_set_valid(self):
        self.sock1.sendline('stance default jiujitsu')
        self.assertIn('Your default bare handed stance is now set to', self.sock1.script)
        self.sock1.sendline('stance')
        self.assertIn('Jiujitsu*', self.sock1.script)
        self.assertIn('Brawling+', self.sock1.script)

    def test_stance_06_current_set_invalid(self):
        self.sock1.sendline('stance ch slinking')
        self.assertIn("don't have a stance like that", self.sock1.script)
        self.sock1.sendline('stance')
        self.assertIn('Jiujitsu*', self.sock1.script)
        self.assertIn('Brawling+', self.sock1.script)

    def test_stance_06_current_set_invalid_weapon(self):
        self.sock1.sendline('stance ch lancer')
        self.assertIn('with the same weapon type as', self.sock1.script)
        self.sock1.sendline('stance')
        self.assertIn('Jiujitsu*', self.sock1.script)
        self.assertIn('Brawling+', self.sock1.script)

    def test_stance_07_current_set_valid(self):
        self.sock1.sendline('stance ch jiujitsu')
        self.assertIn('Your stance is now set to', self.sock1.script)
        self.sock1.sendline('stance')
        self.assertIn('Jiujitsu*+', self.sock1.script)

    def test_money_01_poor(self):
        self.sock1.sendline('wealth')
        self.assertIn('You are carrying no money.', self.sock1.script)

    def test_money_02_rich(self):
        self.p1.money += 500
        self.sock1.sendline('wealth')
        self.assertIn('You currently have 500 ', self.sock1.script)

    def tearDown(self):
        print self.sock1.script
        self.server.flush_pool()
