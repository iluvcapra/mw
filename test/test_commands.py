from typing import assert_never
import unittest
from mw.commands import CommandParser, command_grammar

class TestCommands(unittest.TestCase):
   
    def setUp(self) -> None:
        self.p = CommandParser()
        return super().setUp()

    def test_parse_address(self):
        tree = command_grammar.parse("101")
        result = self.p.visit(tree)

        self.assertIn("in_addr", result.keys())
        self.assertEqual(result["in_addr"], 101)

    def test_parse_2address(self):
        tree = command_grammar.parse(",201")
        result = self.p.visit(tree)

        self.assertIn("out_addr", result.keys())
        self.assertEqual(result["out_addr"], 201)

    def test_parse_12address(self):
        tree = command_grammar.parse("990,1090")
        result = self.p.visit(tree)
        
        self.assertIn("in_addr", result.keys())
        self.assertIn("out_addr", result.keys())
        self.assertEqual(result["in_addr"], 990)
        self.assertEqual(result["out_addr"], 1090)

    def test_parse_action(self):
        tree = command_grammar.parse("xyz")
        result = self.p.visit(tree)

        self.assertIn("action", result.keys())
        self.assertEqual(result["action"], "xyz")

    def test_parse_action2(self):
        tree = command_grammar.parse("change-things")
        result = self.p.visit(tree)

        self.assertIn("action", result.keys())
        self.assertEqual(result["action"], "change-things")

    def test_arglist(self):
        tree = command_grammar.parse("action1 w x100 yz .001 -unimp")
        result = self.p.visit(tree)

        self.assertIn("action", result.keys())
        self.assertEqual(result['action'], 'action1')
        self.assertIn('arguments', result.keys())
        self.assertEqual(result["arguments"], ["w", "x100", "yz", ".001", "-unimp"])

    def test_quoted_args(self):
        tree = command_grammar.parse("ping \"an argument\" x \"John's fuß\" y")
        result = self.p.visit(tree)

        self.assertIn('arguments', result.keys())
        self.assertEqual(result['arguments'], ["an argument", "x", "John's fuß", "y"])

    def test_complicated(self):
        cases = {"100,101 a9 -x +10 \"new file.wav\"": {'in_addr': 100, 
                                                'out_addr': 101, 
                                                'action':'a9',
                                                'arguments':['-x','+10','new file.wav']},
                 "950 cut /a": {'in_addr': 950,
                                'action': 'cut',
                                'arguments': ['/a']},

                 ",2004splat \"Папа Снег\" ...": {'out_addr': 2004,
                                                      'action': 'splat',
                                                      'arguments': ["Папа Снег", "..."]}

                 }

        for k in cases.keys():
            tree = command_grammar.parse(k)
            result = self.p.visit(tree)
            self.assertEqual(result, cases[k])


    def test_empty(self):
        tree = command_grammar.parse("")
        result = self.p.visit(tree)
        self.assertEqual(result, {})

