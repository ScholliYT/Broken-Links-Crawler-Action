import unittest
from unittest.mock import patch
from deadseeker.timer import Timer


class TestTimer(unittest.TestCase):

    def setUp(self):
        self.time_patch = patch('time.time')
        self.time = self.time_patch.start()
        self.time.side_effect = [100.0, 300.0, 800.0, 1300.0, 2300.0]
        # important: don't construct timer until after
        # mocking time...
        self.testobj = Timer()

    def tearDown(self):
        self.time_patch.stop()

    def test_expected_elapsed_after_stop(self):
        self.assertEqual(200.0, self.testobj.stop())

    def test_expect_same_elapsed_after_multiple_stops(self):
        self.testobj.stop()
        self.assertEqual(200.0, self.testobj.stop())


if __name__ == '__main__':
    unittest.main()
