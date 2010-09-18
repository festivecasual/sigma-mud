import unittest

from test import TestbedServer


class TestGetDrop():#unittest.TestCase):
    def setUp(self):
        self.server = TestbedServer()

        self.sock1 = self.server.connection(1)
        self.p1 = self.server.map_login('Apple')
        if not self.p1:
            self.sock1.sendlines('Apple', 'password')
            self.p1 = self.server.map_login('Apple')
            if not self.p1:
                self.sock1.sendlines('new', 'Apple', 'password', '1', '1')
                self.p1 = self.server.map_login('Apple')

        self.sock2 = self.server.connection(2)
        self.p2 = self.server.map_login('Orange')
        if not self.p2:
            self.sock2.sendlines('Orange', 'password')
            self.p2 = self.server.map_login('Orange')
            if not self.p2:
                self.sock2.sendlines('new', 'Orange', 'password', '1', '2')
                self.p2 = self.server.map_login('Orange')

        self.sock3 = self.server.connection(3)
        self.p3 = self.server.map_login('Banana')
        if not self.p3:
            self.sock3.sendlines('Banana', 'password')
            self.p3 = self.server.map_login('Banana')
            if not self.p3:
                self.sock3.sendlines('new', 'Banana', 'password', '2', '2')
                self.p3 = self.server.map_login('Banana')

    def test_getdrop_01_get(self):
        self.sock2.sendline('e')
        self.sock1.sendlines('e', 'get protractor')
        self.assertIn('Apple picks up an Exacto-brand protractor.', self.sock2.script)
        self.assertIn('You pick up an Exacto-brand protractor.', self.sock1.script)

    def test_getdrop_02_drop(self):
        self.sock2.sendline('e')
        self.sock1.sendlines('e', 'drop exacto')
        self.assertIn('Apple drops an Exacto-brand protractor.', self.sock2.script)
        self.assertIn('You drop an Exacto-brand protractor.', self.sock1.script)

    def test_getdrop_03_take(self):
        self.sock2.sendline('e')
        self.sock1.sendlines('e', 'take exacto')
        self.assertIn('Apple picks up an Exacto-brand protractor.', self.sock2.script)
        self.assertIn('You pick up an Exacto-brand protractor.', self.sock1.script)
        self.sock1.sendline('drop exacto')
        self.assertIn('Apple drops an Exacto-brand protractor.', self.sock2.script)
        self.assertIn('You drop an Exacto-brand protractor.', self.sock1.script)

    def test_get_invalid(self):
        self.sock1.sendline('get clue')
        self.assertIn("You can't find it.", self.sock1.script)

    def test_get_stationary(self):
        self.sock1.sendlines('e', 'enter', 'enter', 'get statue')
        self.assertIn("You can't pick that up!", self.sock1.script)

    def test_drop_invalid(self):
        self.sock1.sendline('drop knowledge')
        self.assertIn("You don't have that.", self.sock1.script)

    def test_get_blank(self):
        self.sock1.sendline('get')
        self.assertIn('Get what?', self.sock1.script)

    def test_take_blank(self):
        self.sock1.sendline('take')
        self.assertIn('Take what?', self.sock1.script)

    def test_drop_blank(self):
        self.sock1.sendline('drop')
        self.assertIn('Drop what?', self.sock1.script)

    def tearDown(self):
        print '-------- Apple (socket 1)'
        print self.sock1.script

        print '-------- Orange (socket 2)'
        print self.sock2.script

        print '-------- Banana (socket 3)'
        print self.sock3.script

        self.server.flush_pool()


class TestLookGo():#unittest.TestCase):
    def setUp(self):
        self.server = TestbedServer()

        self.sock1 = self.server.connection(1)
        self.p1 = self.server.map_login('Apple')
        if not self.p1:
            self.sock1.sendlines('Apple', 'password')
            self.p1 = self.server.map_login('Apple')
            if not self.p1:
                self.sock1.sendlines('new', 'Apple', 'password', '1', '1')
                self.p1 = self.server.map_login('Apple')

        self.sock2 = self.server.connection(2)
        self.p2 = self.server.map_login('Orange')
        if not self.p2:
            self.sock2.sendlines('Orange', 'password')
            self.p2 = self.server.map_login('Orange')
            if not self.p2:
                self.sock2.sendlines('new', 'Orange', 'password', '1', '2')
                self.p2 = self.server.map_login('Orange')

        self.sock3 = self.server.connection(3)
        self.p3 = self.server.map_login('Banana')
        if not self.p3:
            self.sock3.sendlines('Banana', 'password')
            self.p3 = self.server.map_login('Banana')
            if not self.p3:
                self.sock3.sendlines('new', 'Banana', 'password', '2', '2')
                self.p3 = self.server.map_login('Banana')

    def test_look(self):
        self.sock1.sendline('look')
        self.assertIn('Unit Test -- Room One', self.sock1.script)
        self.assertIn('Orange is here.', self.sock1.script)

    def test_look_self(self):
        self.sock1.sendline('l self')
        self.assertIn('Apple is here.', self.sock1.script)

    def test_look_direction(self):
        self.sock1.sendline('l e')
        self.assertIn('You see Unit Test -- Room Two in that direction.', self.sock1.script)

    def test_look_player(self):
        self.sock1.sendline('l Orange')
        self.assertIn('Orange is here.', self.sock1.script)

    def test_look_denizen(self):
        self.sock1.sendlines('e', 'e')
        self.assertIn('Melville the Engineer stands before you, wheezing.', self.sock1.script)
        self.assertNotIn('shifts from foot to foot', self.sock1.script)
        self.sock1.sendline('l eng')
        self.assertIn('shifts from foot to foot', self.sock1.script)

    def test_look_item(self):
        self.sock1.sendline('e')
        self.assertIn('An Exacto-brand protractor lies here.', self.sock1.script)
        self.assertNotIn('one-trick pony', self.sock1.script)
        self.sock1.sendline('l prot')
        self.assertIn('one-trick pony', self.sock1.script)

    def test_look_item_alt(self):
        self.sock1.sendline('e')
        self.sock1.sendline('l exacto')
        self.assertIn('one-trick pony', self.sock1.script)

    def test_look_focus(self):
        self.sock1.sendline('l sewer')
        self.assertIn('Hmm...', self.sock1.script)

    def test_look_invalid(self):
        self.sock1.sendline('l melville')
        self.assertIn("You don't see that.", self.sock1.script)

    def test_go_blank(self):
        self.sock1.sendline('go')
        self.assertIn('Where do you want to go?', self.sock1.script)

    def test_go_invalid(self):
        self.sock1.sendline('go kuzey')
        self.assertIn('Where do you want to go?', self.sock1.script)

    def test_go_messaging_standard(self):
        self.sock2.sendline('e')
        self.sock1.sendlines('e', 'e')
        self.assertIn('Apple just went east.', self.sock3.script)
        self.assertIn('Orange just went east.', self.sock3.script)
        self.assertIn('Apple has entered the room.', self.sock2.script)
        self.assertIn('Apple just went east.', self.sock2.script)

    def test_go_messaging_enter(self):
        self.sock1.sendline('e')
        self.sock2.sendlines('e', 'enter')
        self.sock3.sendlines('e', 'enter', 'enter')
        self.assertIn('Orange just went in.', self.sock1.script)
        self.assertIn('Banana just went in.', self.sock2.script)

    def test_go_messaging_leave(self):
        self.sock3.sendlines('e', 'enter', 'enter')
        self.sock2.sendlines('e', 'enter')
        self.sock1.sendline('e')
        self.sock3.sendlines('leave', 'leave')
        self.assertIn('Banana has entered the room.', self.sock2.script)
        self.assertIn('Banana just went out.', self.sock2.script)
        self.assertIn('Banana has entered the room.', self.sock1.script)

    def tearDown(self):
        print '-------- Apple (socket 1)'
        print self.sock1.script

        print '-------- Orange (socket 2)'
        print self.sock2.script

        print '-------- Banana (socket 3)'
        print self.sock3.script

        self.server.flush_pool()


class TestCommunication():#unittest.TestCase):
    def setUp(self):
        self.server = TestbedServer()

        self.sock1 = self.server.connection(1)
        self.p1 = self.server.map_login('Apple')
        if not self.p1:
            self.sock1.sendlines('Apple', 'password')
            self.p1 = self.server.map_login('Apple')
            if not self.p1:
                self.sock1.sendlines('new', 'Apple', 'password', '1', '1')
                self.p1 = self.server.map_login('Apple')

        self.sock2 = self.server.connection(2)
        self.p2 = self.server.map_login('Orange')
        if not self.p2:
            self.sock2.sendlines('Orange', 'password')
            self.p2 = self.server.map_login('Orange')
            if not self.p2:
                self.sock2.sendlines('new', 'Orange', 'password', '1', '2')
                self.p2 = self.server.map_login('Orange')

        self.sock3 = self.server.connection(3)
        self.p3 = self.server.map_login('Banana')
        if not self.p3:
            self.sock3.sendlines('Banana', 'password')
            self.p3 = self.server.map_login('Banana')
            if not self.p3:
                self.sock3.sendlines('new', 'Banana', 'password', '2', '2')
                self.p3 = self.server.map_login('Banana')

    def test_say(self):
        self.sock1.sendline('say Hello to all!')
        self.assertIn("You say, 'Hello to all!'", self.sock1.script)
        self.assertIn("Apple says, 'Hello to all!'", self.sock2.script)

    def test_yell(self):
        self.sock3.sendline('e')
        self.sock1.sendline('yell We are finished here!')
        self.assertIn("You yell, 'We are finished here!'", self.sock1.script)
        self.assertIn("Apple yells, 'We are finished here!'", self.sock2.script)
        self.assertIn("You hear Apple yell, 'We are finished here!'", self.sock3.script)

    def test_emote_custom(self):
        self.sock1.sendline('emote sings in the rain')
        self.assertIn('Apple sings in the rain.', self.sock1.script)
        self.assertIn('Apple sings in the rain.', self.sock2.script)

    def test_emote_solo(self):
        self.sock1.sendline('cackle')
        self.assertIn('You cackle like a maniac!', self.sock1.script)
        self.assertIn('Apple cackles like a maniac!', self.sock2.script)

    def test_emote_directed(self):
        self.sock1.sendline('laugh banana')
        self.assertIn('You laugh at Banana.', self.sock1.script)
        self.assertIn('Apple laughs at Banana.', self.sock2.script)
        self.assertIn('Apple laughs at you.', self.sock3.script)

    def test_emote_misdirected(self):
        self.sock1.sendline('grin pear')
        self.assertIn("They're not here.", self.sock1.script)
        self.assertNotIn('grin', self.sock2.script)
        self.assertNotIn('grin', self.sock3.script)

    def test_emote_nosolo(self):
        self.sock1.sendline('slap')
        self.assertIn("You must specify a target to slap.", self.sock1.script)
        self.assertNotIn('slap', self.sock2.script)

    def test_emote_nodirect_here(self):
        self.sock1.sendline('ponder Orange')
        self.assertIn("You can't do that.", self.sock1.script)
        self.assertNotIn('ponder', self.sock2.script)

    def test_emote_nodirect_absent(self):
        self.sock1.sendline('ponder pear')
        self.assertIn("You can't do that.", self.sock1.script)
        self.assertNotIn('ponder', self.sock2.script)

    def tearDown(self):
        print '-------- Apple (socket 1)'
        print self.sock1.script

        print '-------- Orange (socket 2)'
        print self.sock2.script

        print '-------- Banana (socket 3)'
        print self.sock3.script

        self.server.flush_pool()


class TestOffers():#unittest.TestCase):
    def setUp(self):
        self.server = TestbedServer()

        self.sock1 = self.server.connection(1)
        self.p1 = self.server.map_login('Apple')
        if not self.p1:
            self.sock1.sendlines('Apple', 'password')
            self.p1 = self.server.map_login('Apple')
            if not self.p1:
                self.sock1.sendlines('new', 'Apple', 'password', '1', '1')
                self.p1 = self.server.map_login('Apple')

        self.sock2 = self.server.connection(2)
        self.p2 = self.server.map_login('Orange')
        if not self.p2:
            self.sock2.sendlines('Orange', 'password')
            self.p2 = self.server.map_login('Orange')
            if not self.p2:
                self.sock2.sendlines('new', 'Orange', 'password', '1', '2')
                self.p2 = self.server.map_login('Orange')

        self.sock3 = self.server.connection(3)
        self.p3 = self.server.map_login('Banana')
        if not self.p3:
            self.sock3.sendlines('Banana', 'password')
            self.p3 = self.server.map_login('Banana')
            if not self.p3:
                self.sock3.sendlines('new', 'Banana', 'password', '2', '2')
                self.p3 = self.server.map_login('Banana')

    def test_give_blank_as_give(self):
        self.sock1.sendline('give')
        self.assertIn('Give what?', self.sock1.script)

    def test_give_blank_as_offer(self):
        #TODO: This is not desired behavior, but the operation is correct as-is
        self.sock1.sendline('offer')
        self.assertIn('Give what?', self.sock1.script)

    def test_give_invalid_direct_no_recipient_as_give(self):
        self.sock1.sendline('give clue')
        self.assertIn('Give to whom?', self.sock1.script)

    def test_give_invalid_direct_no_recipient_as_offer(self):
        #TODO: This is not desired behavior, but the operation is correct as-is
        self.sock1.sendline('offer clue')
        self.assertIn('Give to whom?', self.sock1.script)

    def test_give_invalid_direct_valid_recipient(self):
        self.sock1.sendline('give clue orange')
        self.assertIn("You don't have that.", self.sock1.script)

    def test_give_no_recipient_as_give(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('give protractor')
        self.assertIn('Give to whom?', self.sock1.script)
        self.sock1.sendlines('e', 'drop protractor', 'w')

    def test_give_no_recipient_as_offer(self):
        #TODO: This is not desired behavior, but the operation is correct as-is
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('offer protractor')
        self.assertIn('Give to whom?', self.sock1.script)
        self.sock1.sendlines('e', 'drop protractor', 'w')

    def test_give_self_recipient(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('give protractor self')
        self.assertIn('You already have it.', self.sock1.script)
        self.sock1.sendlines('e', 'drop protractor', 'w')

    def test_give_invalid_recipient(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('give protractor reggie')
        self.assertIn("They're not here.", self.sock1.script)
        self.sock1.sendlines('e', 'drop protractor', 'w')

    def test_give_to_invalid_recipient(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('give protractor to reggie')
        self.assertIn("They're not here.", self.sock1.script)
        self.sock1.sendlines('e', 'drop protractor', 'w')

    def test_give_single_offer_full_expiry(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('give protractor orange')
        self.assertIn('You offer an Exacto-brand protractor to Orange.', self.sock1.script)
        self.assertIn('Apple offers an Exacto-brand protractor to you.', self.sock2.script)
        self.assertIn('Apple offers an Exacto-brand protractor to Orange.', self.sock3.script)

        self.sock1.sendline('give protractor orange')
        self.assertIn('You have already offered that to Orange.', self.sock1.script)

        self.server.zip_tasks()
        self.server.run_tasks()
        self.assertIn('You have yet to accept or refuse the offer of an Exacto-brand protractor by Apple.', self.sock2.script)

        self.server.zip_tasks()
        self.server.run_tasks()
        self.assertIn('The offer of an Exacto-brand protractor from Apple can no longer be accepted.', self.sock2.script)
        self.assertIn('Your offer of an Exacto-brand protractor to Orange has been abandoned.', self.sock1.script)

        self.sock2.sendline('accept')
        self.assertIn('You have not been offered anything recently.', self.sock2.script)

        self.sock1.sendlines('e', 'drop protractor', 'w')
        self.assertIn('You drop an Exacto-brand protractor.', self.sock1.script)

    def test_give_single_offer_partial_expiry_refuse(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('offer protractor orange')

        self.server.zip_tasks()
        self.server.run_tasks()
        self.assertIn('You have yet to accept or refuse the offer of an Exacto-brand protractor by Apple.', self.sock2.script)

        self.sock2.sendline('refuse')
        self.assertIn('Orange refuses an Exacto-brand protractor from you.', self.sock1.script)
        self.assertIn('You refuse an Exacto-brand protractor from Apple.', self.sock2.script)
        self.assertIn('Orange refuses an Exacto-brand protractor from Apple.', self.sock3.script)

        self.sock2.sendline('reject')
        self.assertIn('You have not been offered anything recently.', self.sock2.script)

        self.sock1.sendlines('e', 'drop protractor', 'w')
        self.assertIn('You drop an Exacto-brand protractor.', self.sock1.script)

    def test_give_single_offer_partial_expiry_accept(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('offer protractor orange')

        self.server.zip_tasks()
        self.server.run_tasks()
        self.assertIn('You have yet to accept or refuse the offer of an Exacto-brand protractor by Apple.', self.sock2.script)

        self.sock2.sendline('accept')
        self.assertIn('Orange accepts an Exacto-brand protractor from you.', self.sock1.script)
        self.assertIn('You accept an Exacto-brand protractor from Apple.', self.sock2.script)
        self.assertIn('Orange accepts an Exacto-brand protractor from Apple.', self.sock3.script)

        self.sock2.sendline('reject')
        self.assertIn('You have not been offered anything recently.', self.sock2.script)

        self.sock1.sendlines('e', 'drop protractor', 'w')
        self.assertNotIn('You drop an Exacto-brand protractor.', self.sock1.script)

        self.sock2.sendlines('e', 'drop protractor', 'w')
        self.assertIn('You drop an Exacto-brand protractor.', self.sock2.script)

    def test_give_single_offer_immediate_refuse(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('offer protractor orange')

        self.sock2.sendline('refuse')
        self.assertIn('Orange refuses an Exacto-brand protractor from you.', self.sock1.script)
        self.assertIn('You refuse an Exacto-brand protractor from Apple.', self.sock2.script)
        self.assertIn('Orange refuses an Exacto-brand protractor from Apple.', self.sock3.script)

        self.sock2.sendline('reject')
        self.assertIn('You have not been offered anything recently.', self.sock2.script)

        self.sock1.sendlines('e', 'drop protractor', 'w')
        self.assertIn('You drop an Exacto-brand protractor.', self.sock1.script)

    def test_give_single_offer_immediate_accept(self):
        self.sock1.sendlines('e', 'get protractor', 'w')
        self.sock1.sendline('offer protractor orange')

        self.sock2.sendline('accept')
        self.assertIn('Orange accepts an Exacto-brand protractor from you.', self.sock1.script)
        self.assertIn('You accept an Exacto-brand protractor from Apple.', self.sock2.script)
        self.assertIn('Orange accepts an Exacto-brand protractor from Apple.', self.sock3.script)

        self.sock2.sendline('reject')
        self.assertIn('You have not been offered anything recently.', self.sock2.script)

        self.sock1.sendlines('e', 'drop protractor', 'w')
        self.assertNotIn('You drop an Exacto-brand protractor.', self.sock1.script)

        self.sock2.sendlines('e', 'drop protractor', 'w')
        self.assertIn('You drop an Exacto-brand protractor.', self.sock2.script)

    def test_give_multipoint(self):
        self.sock1.sendlines('e', 'get protractor', 'w', 'offer exacto banana', 'offer exacto orange')

        self.assertIn('Apple offers an Exacto-brand protractor to you.', self.sock2.script)
        self.assertIn('Apple offers an Exacto-brand protractor to you.', self.sock3.script)

        self.sock2.sendline('accept')
        self.assertIn('Orange accepts an Exacto-brand protractor from you.', self.sock1.script)
        self.assertIn('You accept an Exacto-brand protractor from Apple.', self.sock2.script)
        self.assertIn('Orange accepts an Exacto-brand protractor from Apple.', self.sock3.script)

        self.sock3.sendline('accept')
        self.assertIn('can no longer be accepted.', self.sock3.script)

        self.sock3.sendline('accept')
        self.assertIn('You have not been offered anything recently.', self.sock3.script)

        self.sock2.sendlines('e', 'drop protractor', 'w')
        self.assertIn('You drop an Exacto-brand protractor.', self.sock2.script)

    def test_accept_no_offers(self):
        self.sock1.sendline('accept')
        self.assertIn('You have not been offered anything recently.', self.sock1.script)

    def tearDown(self):
        print '-------- Apple (socket 1)'
        print self.sock1.script

        print '-------- Orange (socket 2)'
        print self.sock2.script

        print '-------- Banana (socket 3)'
        print self.sock3.script

        self.server.flush_pool()


class TestItems(unittest.TestCase):
    def setUp(self):
        self.server = TestbedServer()

        self.sock1 = self.server.connection(1)
        self.p1 = self.server.map_login('Mango')
        if not self.p1:
            self.sock1.sendlines('Mango', 'password')
            self.p1 = self.server.map_login('Mango')
            if not self.p1:
                self.sock1.sendlines('new', 'Mango', 'password', '1', '1')
                self.p1 = self.server.map_login('Mango')

        self.sock2 = self.server.connection(2)
        self.p2 = self.server.map_login('Honeydew')
        if not self.p2:
            self.sock2.sendlines('Honeydew', 'password')
            self.p2 = self.server.map_login('Honeydew')
            if not self.p2:
                self.sock2.sendlines('new', 'Honeydew', 'password', '1', '1')
                self.p2 = self.server.map_login('Honeydew')

    def test_inventory(self):
        self.sock1.sendlines('e', 'e', 'n', 'i')
        self.assertIn('You are carrying:\r\n    nothing', self.sock1.script)
        self.sock1.sendlines('get token', 'i')
        self.assertIn('You are carrying:\r\n    a token', self.sock1.script)
        self.assertIn('You are wearing:\r\n    nothing', self.sock1.script)
        self.assertIn('You have equipped:\r\n    nothing', self.sock1.script)
        self.sock1.sendline('drop token')
        self.assertIn('You drop a token.', self.sock1.script)

    def test_equip_unequip(self):
        self.sock2.sendlines('e', 'e', 'n')
        self.sock1.sendlines('e', 'e', 'n', 'get token', 'get boots', 'wear boots', 'i')
        self.assertIn('You are carrying:\r\n    a token\r\nYou are wearing:\r\n    a pair of boots', self.sock1.script)
        self.sock1.sendlines('remove boots', 'drop boots', 'drop token')
        self.assertIn('You remove a pair of boots.', self.sock1.script)
        self.assertIn('Mango puts on a pair of boots.', self.sock2.script)
        self.assertIn('Mango removes a pair of boots.', self.sock2.script)

    def test_open_close_valid(self):
        self.sock1.sendline('open d')
        self.assertIn('You open the door.', self.sock1.script)
        self.assertIn('Mango opens the door.', self.sock2.script)
        self.sock1.sendline('close d')
        self.assertIn('You close the door.', self.sock1.script)
        self.assertIn('Mango closes the door.', self.sock2.script)
        self.sock1.sendline('open d')
        self.sock2.sendline('d')
        self.sock1.sendline('close d')
        self.assertIn('The door closes shut.', self.sock2.script)
        self.sock1.sendline('open d')
        self.assertIn('The door opens.', self.sock2.script)
        self.sock1.sendline('close d')

    def test_wield_failure(self):
        self.sock1.sendlines('e', 'e', 'n', 'get stick')
        self.assertIn('You pick up a stick.', self.sock1.script)
        self.sock1.sendline('wield stick')
        self.assertIn("You can't wield a weapon like that!", self.sock1.script)
        self.sock1.sendline('unequip stick')
        self.assertIn("You're not wielding anything like that.", self.sock1.script)
        self.sock1.sendline('drop stick')

    def test_wield(self):
        self.sock1.sendlines('e', 'e', 'n')
        self.sock2.sendlines('e', 'e', 'n', 'get stick')
        self.sock2.sendlines('gm getstance lancer')
        self.sock2.sendline('wield stick')
        self.assertIn('You wield a stick.', self.sock2.script)
        self.assertIn('Honeydew wields a stick.', self.sock1.script)
        self.sock2.sendline('unequip stick')
        self.assertIn('You unequip a stick.', self.sock2.script)
        self.assertIn('Honeydew unequips a stick.', self.sock1.script)
        self.sock2.sendline('drop stick')

    #TODO: Ammo and multiple items (need to clear up some behaviors first)

    def tearDown(self):
        print '-------- Mango (socket 1)'
        print self.sock1.script

        print '-------- Honeydew (socket 2)'
        print self.sock2.script

        self.server.flush_pool()
