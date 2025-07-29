import unittest
from hello_cli import cli
from io import StringIO
import sys

class TestCLI(unittest.TestCase):
    def test_main_output(self):
        captured_output = StringIO()
        sys_stdout_backup = sys.stdout
        sys.stdout = captured_output

        try:
            cli.main()
        finally:
            sys.stdout = sys_stdout_backup

        self.assertEqual(captured_output.getvalue().strip(), "Hi there!")

if __name__ == "__main__":
    unittest.main()
