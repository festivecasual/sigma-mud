import unittest

from archive import Archive
from test import TestbedServer


class TestPlayerSetup(unittest.TestCase):
    def setUp(self):
        self.server = TestbedServer()
        self.sock1 = self.server.connection(1)
        self.p1 = self.server.map_login('First')
        self.flush = True

    def test_01_create_player(self):
        self.sock1.sendlines('new', 'First', 'tester1', '1', '1')
        self.p1 = self.server.map_login('First')
        self.assertTrue(self.p1)
        self.flush = False

    def test_02_player_save(self):
        self.sock1.sendline('save')
        self.assertIn(self.p1.name, Archive().list().keys())
        self.flush = False

    def test_03_player_quit(self):
        self.sock1.sendline('quit')
        self.assertFalse(self.server.map_login('First'))

    def test_04_player_login(self):
        self.sock1.sendlines('First', 'tester1')
        self.assertTrue(self.server.map_login('First'))

    def test_05_player_exit(self):
        self.sock1.sendlines('First', 'tester1')
        self.p1 = self.server.map_login('First')
        self.assertTrue(self.p1)
        self.sock1.sendline('exit')
        self.p1 = self.server.map_login('First')
        self.assertFalse(self.p1)

    def test_create_player_duplicate_name(self):
        self.sock1.sendlines('new', 'First')
        self.p1 = self.server.map_login('First')
        self.assertIn('That name is already taken.', self.sock1.script)

    def test_create_player_blank_name(self):
        self.sock1.sendlines('new', '')
        self.assertIn('You cannot go by that name here.', self.sock1.script)

    def test_create_player_number_name(self):
        self.sock1.sendlines('new', 'Okie123')
        self.assertIn('You cannot go by that name here.', self.sock1.script)

    def test_create_player_uncap_name(self):
        self.sock1.sendlines('new', 'okiedokie')
        self.assertIn('You cannot go by that name here.', self.sock1.script)

    def test_create_player_malicious_name(self):
        self.sock1.sendlines('new', 'Inject\w223\2')
        self.assertIn('You cannot go by that name here.', self.sock1.script)

    def test_create_player_blank_password(self):
        self.sock1.sendlines('new', 'Second', '')
        self.assertIn('Please make your password at least five simple characters.', self.sock1.script)

    def test_create_player_short_password(self):
        self.sock1.sendlines('new', 'Second', '2')
        self.assertIn('Please make your password at least five simple characters.', self.sock1.script)

    def test_create_player_invalid_password(self):
        self.sock1.sendlines('new', 'Second', 'pw&^`~t')
        self.assertIn('Please make your password at least five simple characters.', self.sock1.script)

    def test_create_player_hirange_gender(self):
        self.sock1.sendlines('new', 'Second', 'password', '8')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_lorange_gender(self):
        self.sock1.sendlines('new', 'Second', 'password', '0')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_text_gender(self):
        self.sock1.sendlines('new', 'Second', 'password', 'male')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_blank_gender(self):
        self.sock1.sendlines('new', 'Second', 'password', '')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_negative_gender(self):
        self.sock1.sendlines('new', 'Second', 'password', '-1')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_hirange_race(self):
        self.sock1.sendlines('new', 'Second', 'password', '2', '9')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_lorange_race(self):
        self.sock1.sendlines('new', 'Second', 'password', '2', '0')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_text_race(self):
        self.sock1.sendlines('new', 'Second', 'password', '2', 'Wyvernfolk')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_blank_race(self):
        self.sock1.sendlines('new', 'Second', 'password', '2', '')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def test_create_player_negative_race(self):
        self.sock1.sendlines('new', 'Second', 'password', '2', '-3')
        self.assertIn('Please make a valid choice.', self.sock1.script)

    def tearDown(self):
        print self.sock1.script
        if self.flush:
            self.server.flush_pool()
