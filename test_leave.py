import unittest

from app import LeaveManager


class LeaveManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = LeaveManager({"Alex": 5})

    def test_approves_request_and_updates_balance(self):
        self.assertTrue(self.manager.request_leave("Alex", 3))
        self.assertEqual(self.manager.leaves_left("Alex"), 2)

    def test_rejects_request_when_balance_is_insufficient(self):
        self.assertFalse(self.manager.request_leave("Alex", 6))
        self.assertEqual(self.manager.leaves_left("Alex"), 5)

    def test_approves_request_for_exact_balance(self):
        self.assertTrue(self.manager.request_leave("Alex", 5))
        self.assertEqual(self.manager.leaves_left("Alex"), 0)


if __name__ == "__main__":
    unittest.main()