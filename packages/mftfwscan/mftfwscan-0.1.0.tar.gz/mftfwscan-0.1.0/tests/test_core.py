import unittest
from core import simulate_port_forwarding

class TestCore(unittest.TestCase):
    def test_sftp_rule(self):
        rules = simulate_port_forwarding("SFTP")
        self.assertEqual(rules[0].port, 22)
        self.assertEqual(rules[0].protocol, "TCP")

if __name__ == "__main__":
    unittest.main()
