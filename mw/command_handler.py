import inspect
from copy import deepcopy
import readline

def parse_numeric(base_value: int, val: str):
    if val[0] in ["+","-"] and val[1:].isdigit():
        base_value += int(val)
    elif val.isdigit():
        base_value = int(val)
    return base_value


def completion(partial: str, state: int) -> str:
    obj = CommandHandler()

    all = [name for name in dir(obj) if not f.startswith("__") and f != "handle"]
    begin = [name for name in all if name.startswith(partial)]
    return begin[state]


class CommandHandler:
    
    @classmethod
    def handle(cls, session, words):
        handler = cls()
        if len(words) < 1:
            handler.help(session)
            return

        if hasattr(handler, words[0]):
            getattr(handler, words[0])(session, *words[1:])
        else:
            handler.help(session)
    
    def help(self, stack: 'Stack'):
        "Print help"
        for f in dir(self):
            if not f.startswith("__") and f != "handle":
                m = getattr(self, f)
                argspec = inspect.signature(m)
                if len(argspec.parameters) == 1:
                    print(f"{f}: {m.__doc__}")
                else:
                    pnames = list(argspec.parameters)[1:] 
                    pnames = "[" + ",".join(pnames) + "]"
                    print(f"{f} {pnames} : {m.__doc__}")

    def stack(self, stack: 'Stack'):
        "Print the stack"
        stack.display.print_stack(stack)

    def cmills(self, stack: 'Stack', pos: str = "0"):
        "Set/nudge cursor position in millis"
        stack.cursor = parse_numeric(stack.cursor, pos)
        stack.cursor = min(stack.cursor, stack.length())
        stack.cursor = max(stack.cursor, 0)
        stack.display.print_head(stack)

    def cbegin(self, stack: 'Stack'):
        "Set cursor to beginning of sound"
        stack.cursor = 0
        stack.display.print_head(stack)

    def cend(self, stack: 'Stack'):
        "Set cursor to end of sound"
        if len(stack.stack) > 0:
            stack.cursor = len(stack.stack[-1].segment)
        
        stack.display.print_head(stack)

    def show(self, stack: 'Stack'):
        "Show the current sound"
        stack.display.print_head(stack)

    def i(self, stack: 'Stack', time = None):
        "Set in point"
        new_time = stack.cursor
        if time is not None:
            new_time = parse_numeric(stack.in_point or 0, time)

        stack.in_point = new_time
        stack.display.print_head(stack)

    def o(self, stack: 'Stack', time = None):
        "Set out point"
        new_time = stack.cursor
        if time is not None:
            new_time = parse_numeric(stack.out_point or 0, time)

        stack.out_point = new_time
        stack.display.print_head(stack)

    def setw(self, stack: 'Stack', width = "80"):
        "Set columns width"
        stack.display.display_width = int(width)
        stack.display.print_head(stack)
    
    def dup(self, stack: 'Stack'):
        "Push a copy of the current sound onto the stack"
        sound = deepcopy(stack.stack[-1].segment)
        stack.push_sound(sound)
        stack.display.print_stack(stack)
    
    def swap(self, stack:'Stack'):
        "Swap the top two sounds on the stack"
        if len(stack.stack) > 1:
            stack.stack[-1], stack.stack[-2] = \
                stack.stack[-2], stack.stack[-1]
        
        stack.display.print_stack(stack)

    def pop(self, stack:'Stack'):
        "Pop the top sound on the stack, deleting it"
        stack.stack.pop()
        stack.display.print_stack(stack)
    
    def roll(self, stack:'Stack', count :str = "1"):
        "Roll the stack"
        count = int(count)
        count = count % len(stack.stack)
        stack.stack = stack.stack[count:] + stack.stack[0:count]

    def crop(self, stack: 'Stack',):
        "Crop the sound to the in and out points"
        stack.crop_head()
        stack.display.print_head(stack)

    def ci(self, stack: 'Stack'):
        "Clear in point"
        stack.in_point = None
        stack.display.print_head(stack)

    def co(self, stack:'Stack'):
        "Clear out point"
        stack.out_point = None
        stack.display.print_head(stack)

    def silence(self, stack:'Stack', dur: str):
        "Insert silence at cursor"
        if len(stack.stack) > 0 and dur.isdigit():
            at = stack.cursor
            stack.stack[-1].insert_silence(int(dur), at)
        
        stack.display.print_head(stack)

    def split(self, stack:'Stack'):
        "Split sound"
        if len(stack.stack) > 0:
            stack.split()
        stack.display.print_stack(stack)

    def fadein(self, stack:'Stack'):
        "Fade in from cilp start to cursor"
        pass

    def fadeout(self, stack:'Stack'):
        "Fade out from clip start to cursor"
        pass

    def play(self, stack:'Stack'):
        "Play the sound"
        stack.play()





