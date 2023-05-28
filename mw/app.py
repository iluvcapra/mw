from mw.stack import Stack
from mw.display import Display
from mw.commands import CommandHandler

from os.path import join, split
# from typing import Optional

try:
    import gnureadline as readline
except ImportError:
    import readline


class App:
    display: Display
    stack: Stack
    command_handler: CommandHandler
    should_exit: bool

    def __init__(self):
        self.stack = Stack([])
        self.display = Display()
        self.command_handler = CommandHandler()
        self.should_exit = False
        completer = self.command_handler._partial_completion_handler()
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    def license(self) -> str:
        module_dir = list(split(__file__)[:-2])
        license_path_list = module_dir + ["LICENSE"]
        license_path = join(*license_path_list)
        with open(license_path) as f:
            return f.read()

    def get_input(self):
        selection = []

        if self.stack.top:
            if self.stack.top.in_point is not None:
                selection.append(f"[{self.stack.top.in_point}")

            if self.stack.top.out_point is not None:
                selection.append(f"{self.stack.top.out_point}]")
            
            selection = "→".join(selection)
            return input(f"{self.stack.top.cursor}ms {selection}> ")
        else:
            return input(f"- > ")

    def handle_command_line(self, command):
        if len(command) == 0:
            return

        words = command.split()

        self.command_handler._handle_command(self, words)

    def run(self):
        # print("Type \"q\" to quit.")
        while not self.should_exit:
            command = self.get_input()
            self.handle_command_line(command)

 
