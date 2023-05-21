import inspect
from copy import deepcopy
from typing import List

import mw
from mw.types import Milliseconds

def parse_numeric(base_value: int, val: str):
    if val[0] in ["+","-"] and val[1:].isdigit():
        base_value += int(val)
    elif val.isdigit():
        base_value = int(val)
    return base_value

#
# def completion(obj: 'CommandHandler', partial: str, state: int) -> str:
#     all = [name for name in dir(obj) if not name.startswith("_")]
#     begin = [name for name in all if name.startswith(partial)]
#     return begin[state]
#

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
            getattr(self, words[0])(app, *words[1:])
        else:
            self.help(app)

    def _available_commands(self) -> List[str]:
        return [f for f in dir(self) if not f.startswith("_")]

    def help(self, _ : 'mw.app.App'):
        "Print help"
        for f in self._available_commands(): 
            m = getattr(self, f)
            argspec = inspect.signature(m)
            if len(argspec.parameters) == 1:
                print(f"{f}: {m.__doc__}")
            else:
                pnames = list(argspec.parameters)[1:] 
                pnames = "[" + ",".join(pnames) + "]"
                print(f"{f} {pnames} : {m.__doc__}")

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

    def cbegin(self, app: 'mw.app.App'):
        "Set cursor to beginning of sound"
        if app.stack.top:
            app.stack.top.cursor = Milliseconds(0)
            
        app.display.print_head(app.stack)

    def cend(self, app: 'mw.app.App'):
        "Set cursor to end of sound"
        if app.stack.top:
            app.stack.top.cursor = Milliseconds(len(app.stack.top.segment))
        
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
    
    def roll(self, app:'mw.app.App', count :str = "1"):
        "Roll the stack"
        if count.isdigit():
            num = int(count)
            num = num % len(app.stack.entries)
            app.stack.entries = app.stack.entries[num:] + app.stack.entries[0:num]
        else:
            print(f"Parse error: \"{count}\" is not a number")

    def crop(self, app: 'mw.app.App',):
        "Crop the sound to the in and out points"
        if app.stack.top:
            app.stack.top.crop_to_selection()
        
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
        pass

    def fadeout(self, app:'mw.app.App'):
        "Fade out from clip start to cursor"
        pass

    # def play(self, app:'mw.app.App'):
    #     "Play the sound"
    #     app.play()





