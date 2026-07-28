import unittest
from unittest.mock import patch

from main import main


class TestMain(unittest.TestCase):
    def test_main_exits_immediately(self):
        """Ensure main loop can start and exit without hanging for input."""
        with patch("builtins.input", side_effect=["exit"]), patch("time.sleep", return_value=None):
            try:
                main()
            except Exception as e:
                self.fail(f"main() raised {e} unexpectedly!")


if __name__ == "__main__":
    unittest.main()
