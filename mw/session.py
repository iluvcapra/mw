from pydub import AudioSegment
from pydub.playback import play

from mw.types import Milliseconds
from mw.display import Display
from mw.command_handler import CommandHandler, completion

from typing import List, Optional 
import readline

class StackFrame:
    
    segment: AudioSegment

    def __init__(self, segment: AudioSegment):
            self.segment = segment
    
    def crop(self, start: Milliseconds, end: Milliseconds):
        assert end > start, "crop end must be > crop start"
        self.segment = self.segment[start:end]
    
    def insert_silence(self, duration: Milliseconds, at: Milliseconds):
        a = self.segment[0:at]
        b = self.segment[at:]
        silence = AudioSegment.silent(duration=duration)
        self.segment = a + silence + b 

    def clip(self) -> AudioSegment:
        return self.segment


class Session:
    stack: List[StackFrame]
    display: Display
    in_point: Optional[Milliseconds]
    out_point: Optional[Milliseconds]

    def __init__(self, segments : List[AudioSegment]):
        self.stack = []
        self.display = Display()
        self.cursor = 0
        self.in_point = None
        self.out_point = None
        for segment in segments:
            self.push_sound(segment)
        
        readline.set_completer(completion)
        readline.parse_and_bind("tab: complete")


    def push_sound(self, segment: AudioSegment):
        print(f"Pushing audio ({len(segment)} ms) onto stack...")
        self.stack.append(StackFrame(segment=segment))
        self.display.view_start = 0
        self.display.view_end = self.length()
    
    def crop_head(self):
        if len(self.stack) > 0:
            frame = self.stack[-1]
            self.stack[-1].crop(self.in_point or 0, 
                                self.out_point or len(frame.clip()))
        self.in_point = None
        self.out_point = None
        self.cursor = 0

    def split(self):
        if len(self.stack) > 0:
            to_split = self.stack[-1].segment
            a = to_split[0:self.cursor]
            b = to_split[self.cursor:]
            self.stack.pop()
            self.stack.append(StackFrame(a))
            self.stack.append(StackFrame(b))

        self.cursor = 0
        self.in_point = None
        self.out_point = None
        self.display.view_start = 0
        self.display.view_end = self.length()

    def play(self):
        if len(self.stack) > 0:
            play(self.stack[-1].segment)

        
        

    def length(self) -> Milliseconds:
        return max(map(lambda x: len(x.clip()), self.stack))

    def get_input(self):
        selection = []
        if self.in_point is not None:
            selection.append(f"[{self.in_point}")

        if self.out_point is not None:
            selection.append(f"{self.out_point}]")
        
        selection = "→".join(selection)
        return input(f"{self.cursor}ms {selection}> ")
    
    def handle_command(self, command):
        words = command.split()
        if words[0] == 'q':
            return False
        else:
            CommandHandler.handle(self, words)

        return True

    def run(self):
        self.display.print_stack(self)
        while True:
            command = self.get_input()
            if not self.handle_command(command):
                break


    
