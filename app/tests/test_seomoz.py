from nose import tools


class TestSEOMoz(object):

  def setUp(self):
    print "setup"

  def tearDown(self):
    print "teardown"

  def test_one(self):
    print "test_one"
    tools.assert_true(1)

  def test_two(self):
    print "test_two"
    tools.assert_true(1)
  