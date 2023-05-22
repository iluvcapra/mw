from mw.stack import Stack
from mw.display import Display
from mw.command_handler import CommandHandler

from typing import Optional

try:
    import gnureadline as readline
except ImportError:
    import readline


class App:
    display: Display
    stack: Stack
    command_handler: CommandHandler

    def __init__(self):
        self.stack = Stack([])
        self.display = Display()
        self.command_handler = CommandHandler()
        completer =  self.command_handler._partial_completion_handler()
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")


    def get_input(self):
        selection = []

        if self.stack.top:
            if self.stack.top.in_point:
                selection.append(f"[{self.stack.top.in_point}")

            if self.stack.top.out_point:
                selection.append(f"{self.stack.top.out_point}]")
            
            selection = "→".join(selection)
            return input(f"{self.stack.top.cursor}ms {selection}> ")
        else:
            return input(f"- > ")

    def handle_command(self, command):
        if len(command) == 0:
            return True

        words = command.split()

        if words[0] == 'q':
            return False
        else:
            self.command_handler._handle(self, words)

        return True

    def run(self):
        self.display.print_stack(self.stack)
        while True:
            command = self.get_input()
            if not self.handle_command(command):
                break

 
