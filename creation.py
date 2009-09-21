from common import *


classes = {}
races = {}


class character_class(object):
    def __init__(self, node):
        self.name = strip_whitespace(required_child(node, 'name').text)
        self.desc = wordwrap(strip_whitespace(required_child(node, 'desc').text))
        self.background = wordwrap(strip_whitespace(required_child(node, 'background').text))
        # TODO 'stats' 'paths' 'skills'
