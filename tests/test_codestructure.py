import unittest
import os.path
from glob import glob
from string import whitespace


class TestCodeQuality(unittest.TestCase):
    def setUp(self):
        pass

    def test_trailing_main(self):
        [self.check_trailing(source) for source in glob('*.py')]

    def test_trailing_handlers(self):
        [self.check_trailing(source) for source in glob(os.path.join('handlers', '*.py'))]

    def test_trailing_tasks(self):
        [self.check_trailing(source) for source in glob(os.path.join('tasks', '*.py'))]

    def test_trailing_tests(self):
        [self.check_trailing(source) for source in glob(os.path.join('tests', '*.py'))]

    def test_trailing_xml(self):
        [self.check_trailing(source) for source in glob(os.path.join('config', '*.xml'))]

    def test_trailing_xml_areas(self):
        [self.check_trailing(source) for source in glob(os.path.join('config', 'areas', '*.xml'))]

    def test_tabs_main(self):
        [self.check_tabs(source) for source in glob('*.py')]

    def test_tabs_handlers(self):
        [self.check_tabs(source) for source in glob(os.path.join('handlers', '*.py'))]

    def test_tabs_tasks(self):
        [self.check_tabs(source) for source in glob(os.path.join('tasks', '*.py'))]

    def test_tabs_tests(self):
        [self.check_tabs(source) for source in glob(os.path.join('tests', '*.py'))]

    def test_tabs_xml(self):
        [self.check_tabs(source) for source in glob(os.path.join('config', '*.xml'))]

    def test_tabs_xml_areas(self):
        [self.check_tabs(source) for source in glob(os.path.join('config', 'areas', '*.xml'))]

    def check_trailing(self, source):
        with open(source, 'r') as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]
            for i, l in zip(range(1, len(lines)+1), lines):
                self.assertTrue(l == l.rstrip(whitespace), 'Trailing whitespace in %s:%d' % (source, i))

    def check_tabs(self, source):
        with open(source, 'r') as f:
            lines = [line.rstrip('\r\n') for line in f.readlines()]
            for i, l in zip(range(1, len(lines)+1), lines):
                self.assertTrue(l == l.strip('\t'), 'Tab found in %s:%d' % (source, i))

    def tearDown(self):
        pass
