import inspect
from copy import deepcopy
from typing import List, Callable, Optional

import mw
from mw.types import Milliseconds

from parsimonious.exceptions import IncompleteParseError
from parsimonious.grammar import Grammar
from parsimonious import NodeVisitor


command_grammar = Grammar(
    r"""
    command = number? ("," number)? (sep? action arglist)? 
    arglist = (sep argument)*
    argument = (quoted / word)
    quoted = quote literal quote
    action = ~r"[A-z]+[A-z0-9\-]*"
    number = ~r"-?[\d]+"
    word = ~r"\S+"
    quote = "\""
    literal = ~r"[^\"]*"
    sep = ~r"\s+"
    """)

class CommandParser(NodeVisitor):
    def visit_command(self, _, visited_children):
        start_part, end_part, imperative_part = visited_children

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
    The command handler implements commands originating from the prompt. The App
    parses command lines into words and then hands these to the handler's _handle method.
    The first word is the command name, and a attribute with a matching name is searched in
    the CommandHandler instance. If a match isn't found, the "help" method is run.

    If a match IS found, the corresponding attribute is called, with the App instance
    passed as the first parameter. If any additional words were present on the command line, 
    they are passed as strings afterward.

    The help() method iterates through all the "normal" named attributes on the class 
    and prints the docstring for each as the help text.
    """
    _command_in: Optional[Milliseconds]
    _command_out: Optional[Milliseconds]

    def __init__(self):
        self._parser_grammar = command_grammar
        self._parser_visitor = CommandParser()
        
    def _handle_command(self, app: 'mw.app.App', command: str): 
        self._command_in = None
        self._command_out = None
        
        try: 
            command_dict = self._parser_visitor.visit(self._parser_grammar.parse(command))
        except IncompleteParseError as e:
            print(f"Error: Command could not be parsed.")
            return
        
        if app.stack.top is not None:
            self._command_in = app.normalize_command_time(
                command_dict.get('in_addr', app.stack.top.in_point or 0))

            self._command_out = app.normalize_command_time(
                command_dict.get('out_addr', app.stack.top.out_point or -1))
            
            if 'in_addr' in command_dict:
                app.stack.top.in_point = self._command_in

            if 'out_addr' in command_dict:
                app.stack.top.out_point = self._command_out

            if self._command_in is not None and self._command_out is not None and self._command_out < self._command_in:
                self._command_in, self._command_out = self._command_out, self._command_in

        if 'action' in command_dict.keys():
            if command_dict['action'] in self._available_commands():

                try:
                    args = command_dict.get('arguments', [])
                    getattr(self, command_dict['action'])(app, *args)
                except TypeError:
                    print(f"Error: action {command_dict['action']} called with incorrect argument list.")
            else:
                print(f"Error: action {command_dict['action']} is not recognized.")


    def _available_commands(self) -> List[str]:
        return [f for f in dir(self) if not f.startswith("_")]

    def _partial_completion_handler(self) -> Callable[[str, int],Optional[str]]:
        def _impl_autocomplete(partial: str, state: int) -> Optional[str]:
            possible = [name for name in self._available_commands() if name.startswith(partial)]
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

    # def cmills(self, app: 'mw.app.App', pos: str = "0"):
    #     "Set/nudge cursor position in millis"
    #     if app.stack.top:
    #         app.stack.top.cursor = Milliseconds(parse_numeric(app.stack.top.cursor, pos))
    #         app.stack.top.cursor = Milliseconds(min(app.stack.top.cursor, len(app.stack.top.segment)))
    #         app.stack.top.cursor = Milliseconds(max(app.stack.top.cursor, 0))
    #         app.display.print_head(app.stack)

    # def cend(self, app: 'mw.app.App', pos: str = "0"):
    #     "Set cursor relative to the end of sound"
    #     if app.stack.top:
    #         val = parse_numeric(0, pos)
    #         new_time = len(app.stack.top.segment) - abs(val)
    #         app.stack.top.cursor = Milliseconds(new_time)
    #     
    #     app.display.print_head(app.stack)

    def show(self, app: 'mw.app.App'):
        "Show the current sound"
        app.display.print_head(app.stack)

    # def i(self, app: 'mw.app.App', time = None):
    #     "Set in point"
    #     if app.stack.top:
    #         new_time = app.stack.top.cursor
    #         if time:
    #             new_time = parse_numeric(app.stack.top.in_point or 0, time)
    #         
    #         app.stack.top.in_point = Milliseconds(new_time)
    #         app.display.print_head(app.stack)
    #
    # def o(self, app: 'mw.app.App', time = None):
    #     "Set out point"
    #     if app.stack.top:
    #         new_time = app.stack.top.cursor
    #         if time:
    #             new_time = parse_numeric(app.stack.top.out_point or 0, time)
    #         
    #         app.stack.top.out_point = Milliseconds(new_time)
    #         app.display.print_head(app.stack)

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
                app.stack.entries = app.stack.entries[-1:] + app.stack.entries[0:-1]
        else:
            print(f"Parse error: \"{count}\" is not a number")

    def crop(self, app: 'mw.app.App',):
        "Crop the sound to the in and out points"
        if app.stack.top:
            assert self._command_in is not None
            assert self._command_out is not None
            app.stack.top.crop(self._command_in, self._command_out)
        
        app.display.print_head(app.stack)

    def silence(self, app:'mw.app.App', dur: str):
        "Insert silence at in-point"
        if dur.isdigit():
            if app.stack.top:
                at = app.stack.top.cursor
                app.stack.top.insert_silence(Milliseconds(int(dur)), at)
            
            app.display.print_head(app.stack)
        else:
            print(f"Parse error: \"{dur}\" is not a number")

    def split(self, app:'mw.app.App'):
        "Split sound"
        if app.stack.top:
            app.stack.split()
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

    def fadein(self, app:'mw.app.App'):
        "Fade in from cilp start to cursor"
        if app.stack.top:
            app.stack.top.fade_in(app.stack.top.cursor)

        app.display.print_head(app.stack)

    def fadeout(self, app:'mw.app.App'):
        "Fade out from clip start to cursor"
        if app.stack.top:
            app.stack.top.fade_out(app.stack.top.cursor)
        
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
        if app.stack.top and (app.stack.top.in_point is not None 
            or app.stack.top.out_point is not None):

            app.stack.top.bloop()

        app.display.print_head(app.stack)

    def export(self, app: 'mw.app.App', name: str = "out.wav"):
        "Export audio as a wav file"
        if app.stack.top:
            app.stack.top.export(name)

