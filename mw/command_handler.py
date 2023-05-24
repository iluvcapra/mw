import inspect
from copy import deepcopy
from typing import List, Callable, Optional
import sys, os

import mw
from mw.types import Milliseconds

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
    def _handle(self, app, words): 
        if len(words) > 0 and hasattr(self, words[0]):
            try:
                getattr(self, words[0])(app, *words[1:])
            except TypeError:
                print("Error: incorrect parameter count to command")
        else:
            self.help(app)

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

    def cmills(self, app: 'mw.app.App', pos: str = "0"):
        "Set/nudge cursor position in millis"
        if app.stack.top:
            app.stack.top.cursor = Milliseconds(parse_numeric(app.stack.top.cursor, pos))
            app.stack.top.cursor = Milliseconds(min(app.stack.top.cursor, len(app.stack.top.segment)))
            app.stack.top.cursor = Milliseconds(max(app.stack.top.cursor, 0))
            app.display.print_head(app.stack)

    def cend(self, app: 'mw.app.App', pos: str = "0"):
        "Set cursor relative to the end of sound"
        if app.stack.top:
            val = parse_numeric(0, pos)
            new_time = len(app.stack.top.segment) - abs(val)
            app.stack.top.cursor = Milliseconds(new_time)
        
        app.display.print_head(app.stack)

    def show(self, app: 'mw.app.App'):
        "Show the current sound"
        app.display.print_head(app.stack)

    def i(self, app: 'mw.app.App', time = None):
        "Set in point"
        if app.stack.top:
            new_time = app.stack.top.cursor
            if time:
                new_time = parse_numeric(app.stack.top.in_point or 0, time)
            
            app.stack.top.in_point = Milliseconds(new_time)
            app.display.print_head(app.stack)

    def o(self, app: 'mw.app.App', time = None):
        "Set out point"
        if app.stack.top:
            new_time = app.stack.top.cursor
            if time:
                new_time = parse_numeric(app.stack.top.out_point or 0, time)
            
            app.stack.top.out_point = Milliseconds(new_time)
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
                app.stack.entries = app.stack.entries[-1:] + app.stack.entries[0:-1]
        else:
            print(f"Parse error: \"{count}\" is not a number")

    def crop(self, app: 'mw.app.App',):
        "Crop the sound to the in and out points"
        if app.stack.top:
            app.stack.top.crop_to_selection()
        
        app.display.print_head(app.stack)

    def silence(self, app:'mw.app.App', dur: str):
        "Insert silence at cursor"
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
        if app.stack.top:
            app.stack.top.export(name)




