from unittest.mock import MagicMock 
from unittest import TestCase

from mw import commands
from mw.app import App
from mw.display import Display
from mw.stack import Stack


class TestCommands(TestCase):
    def setUp(self) -> None:
        self.mock_app = MagicMock(spec=App)
        self.mock_app.display = MagicMock(spec=Display)
        self.mock_app.stack = MagicMock(spec=Stack)
        self.command_handler = commands.CommandHandler()
        return super().setUp()

    def tearDown(self) -> None:
        self.mock_app.reset_mock()
        self.mock_app.display.reset_mock()
        self.mock_app.stack.reset_mock()
        return super().tearDown()
    
    # def test_license(self):
    #     self.command_handler.license(self.mock_app)
    #     self.mock_app.license.assert_called()
    
    def test_help(self):
        self.command_handler.help(self.mock_app)

 
