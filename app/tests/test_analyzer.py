from nose import tools

"""
tools.assert_equals
tools.assert_true
"""


class TestKeywordAnalyzer(object):
    def setUp(self):
        self.h = "init"
        
    def tearDown(self):
        self.h = None

    def test_true(self):
        tools.assert_true(True)
