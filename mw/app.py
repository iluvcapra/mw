from mw.stack import Stack
from mw.display import Display
from mw.command_handler import CommandHandler, completion

import readline


class App:
    display: Display
    stack: Stack

    def __init__(self):
        self.stack = Stack([])
        self.display = Display()
        readline.set_completer(completion)
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
        words = command.split()
        if words[0] == 'q':
            return False
        else:
            CommandHandler._handle(self, words)

        return True

    def run(self):
        self.display.print_stack(self.stack)
        while True:
            command = self.get_input()
            if not self.handle_command(command):
                break

 
