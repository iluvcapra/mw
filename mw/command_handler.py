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
    
    def help(self, session: 'Session'):
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

    def stack(self, session: 'Session'):
        "Print the stack"
        session.display.print_stack(session)

    def cm(self, session: 'Session', pos: str = "0"):
        "Set/nudge cursor position in millis"
        session.cursor = parse_numeric(session.cursor, pos)
        session.cursor = min(session.cursor, session.length())
        session.cursor = max(session.cursor, 0)
        session.display.print_head(session)

    def cbegin(self, session: 'Session'):
        "Set cursor to beginning of sound"
        session.cursor = 0
        session.display.print_head(session)

    def cend(self, session: 'Session'):
        "Set cursor to end of sound"
        if len(session.stack) > 0:
            session.cursor = len(session.stack[-1].segment)
        
        session.display.print_head(session)


    def show(self, session: 'Session'):
        "Show the current sound"
        session.display.print_head(session)

    def i(self, session: 'Session', time = None):
        "Set in point"
        new_time = session.cursor
        if time is not None:
            new_time = parse_numeric(session.in_point or 0, time)

        session.in_point = new_time
        session.display.print_head(session)

    def o(self, session: 'Session', time = None):
        "Set out point"
        new_time = session.cursor
        if time is not None:
            new_time = parse_numeric(session.out_point or 0, time)

        session.out_point = new_time
        session.display.print_head(session)

    def setw(self, session: 'Session', width = "80"):
        "Set columns width"
        session.display.display_width = int(width)
        session.display.print_head(session)
    
    def dup(self, session: 'Session'):
        "Push a copy of the current sound onto the stack"
        sound = deepcopy(session.stack[-1].segment)
        session.push_sound(sound)
        session.display.print_stack(session)
    
    def swap(self, session:'Session'):
        "Swap the top two sounds on the stack"
        if len(session.stack) > 1:
            session.stack[-1], session.stack[-2] = \
                session.stack[-2], session.stack[-1]
        
        session.display.print_stack(session)

    def pop(self, session:'Session'):
        "Pop the top sound on the stack, deleting it"
        session.stack.pop()
        session.display.print_stack(session)

    def crop(self, session: 'Session',):
        "Crop the sound to the in and out points"
        session.crop_head()
        session.display.print_head(session)

    def ci(self, session: 'Session'):
        "Clear in point"
        session.in_point = None
        session.display.print_head(session)

    def co(self, session:'Session'):
        "Clear out point"
        session.out_point = None
        session.display.print_head(session)

    def silence(self, session:'Session', dur: str):
        "Insert silence at cursor"
        if len(session.stack) > 0 and dur.isdigit():
            at = session.cursor
            session.stack[-1].insert_silence(int(dur), at)
        
        session.display.print_head(session)





