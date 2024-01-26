import inspect
from copy import deepcopy
from typing import List, Callable, Optional

import mw
from mw.types import Decibels, Milliseconds

from parsimonious.exceptions import IncompleteParseError
from parsimonious.grammar import Grammar
from parsimonious import NodeVisitor


command_grammar = Grammar(
    r"""
    command = number? ("," number)? (sep? action arglist)? (sep* "#" comment)? 
    arglist = (sep argument)*
    argument = (quoted / word)
    quoted = quote literal quote
    action = ~r"[A-z]+[A-z0-9\-]*"
    number = ~r"-?[\d]+"
    word = ~r"[^\s#]+"
    quote = "\""
    comment = ~r".*"
    literal = ~r"[^\"#]*"
    sep = ~r"\s+"
    """)

class CommandParser(NodeVisitor):
    def visit_command(self, _, visited_children):
        start_part, end_part, imperative_part, _ = visited_children

        retval = {}
        
        for start in start_part:
            retval['in_addr'] = start

        for end in end_part:
            _, retval['out_addr'] = end

        for imperative in imperative_part:
            _, retval['action'], arg_list = imperative
            retval['arguments'] = arg_list
 
        return retval
    
    def visit_arglist(self, _, visited_children) -> List[str]:
        repeating_args = visited_children

        retval = []
        for arg_form in repeating_args:
            _, arg = arg_form
            retval.append(arg[0])

        return retval

    def visit_number(self, node, _) -> int:
        return int(node.text)

    def visit_action(self, node, _) -> str:
        return node.text

    def visit_word(self, node, _) -> str:
        return node.text

    def visit_quoted(self, _, visited_children) -> str:
        _, word, _ = visited_children
        return word.text

    def generic_visit(self, node, visited_children):
        return visited_children or node


def parse_numeric(base_value: int, val: str):
    """
    A helper function for converting numeric entries from the command prompt.
    """
    if val[0] in ["+","-"] and val[1:].isdigit():
        base_value += int(val)
    elif val.isdigit():
        base_value = int(val)
    return base_value


class CommandHandler:
    """
    The command handler implements commands originating from the prompt. The 
    App parses command lines into words and then hands these to the handler's 
    _handle method. The first word is the command name, and a attribute with a 
    matching name is searched in the CommandHandler instance. If a match isn't 
    found, the "help" method is run.

    If a match IS found, the corresponding attribute is called, with the App 
    instance passed as the first parameter. If any additional words were 
    present on the command line, they are passed as strings afterward.

    The help() method iterates through all the "normal" named attributes on the 
    class and prints the docstring for each as the help text.
    """
    _effective_in: Optional[Milliseconds]
    _effective_out: Optional[Milliseconds]

    def __init__(self):
        self._parser_grammar = command_grammar
        self._parser_visitor = CommandParser()
    
    def _handle_command(self, app: 'mw.app.App', command: str): 
        
        try: 
            command_dict = self._parser_visitor.visit(
                self._parser_grammar.parse(command)
            )
        except IncompleteParseError as e:
            print(f"Error: Command could not be parsed.")
            return

        self._effective_in = None
        self._effective_out = None        
        
        if app.stack.top is not None:
            self._effective_in = app.normalize_command_time(
                command_dict.get('in_addr', app.stack.top.in_point or 0))

            self._effective_out = app.normalize_command_time(
                command_dict.get('out_addr', app.stack.top.out_point or -1))
            
            if 'in_addr' in command_dict:
                app.stack.top.in_point = self._effective_in

            if 'out_addr' in command_dict:
                app.stack.top.out_point = self._effective_out

            if self._effective_in is not None \
                and self._effective_out is not None \
                and self._effective_out < self._effective_in:
                self._effective_in, self._effective_out = \
                self._effective_out, self._effective_in

        if 'action' in command_dict.keys():
            if command_dict['action'] in self._available_commands():

                # try:
                args = command_dict.get('arguments', [])
                getattr(self, command_dict['action'])(app, *args)
                # except TypeError:
                #     print(f"Error: action {command_dict['action']} called 
                #     with incorrect argument list.")
            else:
                print(f"Error: action {command_dict['action']} " 
                      f"is not recognized.")


    def _available_commands(self) -> List[str]:
        return [f for f in dir(self) if not f.startswith("_")]

    def _partial_completion_handler(self) -> Callable[[str, int],Optional[str]]:
        def _impl_autocomplete(partial: str, state: int) -> Optional[str]:
            possible = [name for name in self._available_commands() \
                if name.startswith(partial)]
            if len(possible) > 0:
                return possible[state]
            else:
                return None

        return _impl_autocomplete

    def q(self, app: 'mw.app.App'):
        "Exit the program"
        app.should_exit = True

    def help(self, _ : 'mw.app.App'):
        "Print help"
        for f in self._available_commands(): 
            m = getattr(self, f)
            argspec = inspect.signature(m)
            if len(argspec.parameters) == 1:
                print(f"{f:15}: {m.__doc__}")
            else:
                pnames = list(argspec.parameters)[1:] 
                pnames = "[" + ",".join(pnames) + "]"
                print(f"{f} {pnames}".ljust(15) + f": {m.__doc__}")
    
    def license(self, app: 'mw.app.App'):
        "Print the license"
        print(app.license())
 
    def stack(self, app: 'mw.app.App'):
        "Print the stack"
        app.display.print_stack(app.stack)

    def show(self, app: 'mw.app.App'):
        "Show the current sound"
        app.display.print_head(app.stack)

    def ci(self, app: 'mw.app.App'):
        "Clear in point"
        if app.stack.top:
            app.stack.top.in_point = None

        app.display.print_head(app.stack)

    def co(self, app:'mw.app.App'):
        "Clear out point"
        if app.stack.top:
            app.stack.top.out_point = None

        app.display.print_head(app.stack)
    def setw(self, app: 'mw.app.App', width = "80"):
        "Set columns width"
        app.display.display_width = int(width)
        app.display.print_head(app.stack)
    
    def dup(self, app: 'mw.app.App'):
        "Push a copy of the current sound onto the stack"
        if app.stack.top:
            sound = deepcopy(app.stack.top.segment)
            app.stack.push_sound(sound)
            app.display.print_stack(app.stack)
    
    def swap(self, app:'mw.app.App'):
        "Swap the top two sounds on the stack"
        if len(app.stack.entries) > 1:
            app.stack.entries[-1], app.stack.entries[-2] = \
                app.stack.entries[-2], app.stack.entries[-1]
        
        app.display.print_stack(app.stack)

    def pop(self, app:'mw.app.App'):
        "Pop the top sound on the stack, deleting it"
        app.stack.entries.pop()
        app.display.print_stack(app.stack)
    
    def roll(self, app:'mw.app.App', count: str = "1"):
        "Roll the stack"
        if count.isdigit() or count[0] == "-" and count[1:].isdigit():
            num = int(count)
            num = num % len(app.stack.entries)
            for _ in range(num):
                app.stack.entries = app.stack.entries[-1:] + \
                    app.stack.entries[0:-1]
        else:
            print(f"Parse error: \"{count}\" is not a number")

    def crop(self, app: 'mw.app.App',):
        "Crop the sound to the in and out points"
        if app.stack.top:
            assert self._effective_in is not None
            assert self._effective_out is not None
            app.stack.top.crop(self._effective_in, self._effective_out)
        
        app.display.print_head(app.stack)

    def silence(self, app:'mw.app.App'):
        "Insert silence at in-point"
        if app.stack.top:
            assert self._effective_out is not None
            assert self._effective_in is not None
            app.stack.top.insert_silence(
                Milliseconds(self._effective_out - self._effective_in),  
                self._effective_in)
        
        app.display.print_head(app.stack)

    def new(self, app:'mw.app.App', length = "1000"):
        "Creates a new sound of [length] milliseconds"
        app.stack.create_new(length=Milliseconds(int(length)))

    def split(self, app:'mw.app.App'):
        "Split sound"
        if app.stack.top:
            assert self._effective_in is not None
            app.stack.split(self._effective_in)
        app.display.print_stack(app.stack)

    def append(self, app:'mw.app.App'):
        "Append sound"
        if len(app.stack.entries) > 1:
            app.stack.append()
        app.display.print_stack(app.stack)

    def prepend(self, app:'mw.app.App'):
        "Prepend sound"
        if len(app.stack.entries) > 1:
            app.stack.prepend()
        app.display.print_stack(app.stack)

    def loop(self, app:'mw.app.App', count = "2"):
        "Loop sound"
        if app.stack.top:
            app.stack.loop(count=int(count))
        app.display.print_head(app.stack)
    
    def normalize(self, app:'mw.app.App', level = "0.0"):
        "Normalize sound to [level] dB"
        if app.stack.top:
            assert self._effective_in is not None
            assert self._effective_out is not None

            app.stack.top.normalize(self._effective_in, 
                                    self._effective_out, 
                                    Decibels(float(level)))

        app.display.print_head(app.stack)


    def fadein(self, app:'mw.app.App'):
        "Fade in from cilp start to in point"
        if app.stack.top:
            assert self._effective_in is not None
            app.stack.top.fade_in(self._effective_in)

        app.display.print_head(app.stack)

    def fadeout(self, app:'mw.app.App'):
        "Fade out from out point to end of file"
        if app.stack.top:
            assert self._effective_out is not None 
            app.stack.top.fade_out(self._effective_out)
        
        app.display.print_head(app.stack)

    def play(self, app:'mw.app.App'):
        "Play the sound"
        if app.stack.top:
            app.stack.top.play()
    
    def length(self, app:'mw.app.App'):
        "Print the length of the top sound"
        if app.stack.top:
            print(f"{len(app.stack.top.segment)} ms")

    def bounce(self, app: 'mw.app.App'):
        "Bounce (mix) the top sound in the stack with the sound below it"
        if len(app.stack.entries) > 1:
            app.stack.bounce()

        app.display.print_stack(app.stack)

    def bloop(self, app: 'mw.app.App'):
        "Replace audio in selection with silence"
        if app.stack.top:
            assert self._effective_in is not None
            assert self._effective_out is not None

            app.stack.top.bloop(
                Milliseconds(self._effective_out - self._effective_in),                  
                self._effective_in
            )

        app.display.print_head(app.stack)

    def export(self, app: 'mw.app.App', name: str = "out.wav"):
        "Export audio as a wav file"
        if app.stack.top:
            app.stack.top.export(name)

