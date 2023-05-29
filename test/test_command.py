from unittest.mock import MagicMock
from unittest import TestCase

from mw import commands

class TestCommands(TestCase):
    def setUp(self) -> None:
        self.mock_app = MagicMock()
        self.mock_app.display = MagicMock()
        self.mock_app.stack = MagicMock()
        self.command_handler = commands.CommandHandler()
        return super().setUp()

    def tearDown(self) -> None:
        self.mock_app.reset_mock()
        self.mock_app.display.reset_mock()
        self.mock_app.stack.reset_mock()
        return super().tearDown()

    def test_show(self):
        self.command_handler.show(self.mock_app)
        self.mock_app.display.print_head.assert_called()
    
    def test_license(self):
        self.command_handler.license(self.mock_app)
        self.mock_app.license.assert_called()

    def test_swap(self):
        self.command_handler.swap(self.mock_app)
        # self.mock_app.stack.swap.assert_called()

     
        
