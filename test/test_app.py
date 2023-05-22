import unittest

from mw.app import App

class TestApp(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_create(self):
        app = App()
        assert app is not None
