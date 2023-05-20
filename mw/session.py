from pydub import AudioSegment
# from apeek import WaveformData, unicode_waveform

from mw.types import Milliseconds
from mw.display import Display

from collections import deque
from typing import List, Optional


class StackFrame:
    segment: AudioSegment

    def __init__(self, segment: AudioSegment):
            self.segment = segment
    
    def crop(self, start: Milliseconds, end: Milliseconds):
        assert end > start, "crop end must be > crop start"
        self.segment = self.segment[start:end]

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
        self.display.print_head(self)

    def delay_head(self):
        pass

    def parse_numeric(self, base_value: int, val: str):
        if val[0] in ["+","-"] and val[1:].isdigit():
            base_value += int(val)
        elif val.isdigit():
            base_value = int(val)
        return base_value

    def length(self) -> Milliseconds:
        return max(map(lambda x: len(x.clip()), self.stack))

    def get_input(self):
        return input("> ")

    def handle_command(self, command):
        words = command.split()
        if words[0] == 'q':
            return False
        elif words[0] in ['h','?','help']:
            print("q: quit")
            print("cm [int]: set cursor pos (millis)")
            print("i: set in point")
            print("o: set out point")
            print("x: clear in, out")
            print("k: crop sound to in, out")
            print("d []: delay start")
            print("v: show view info")
            print("h: show this message")
            print("stack: print stack")
            print("s: print head of stack")
            print("p: pop stack")
            print("setw [int]: set display width")
        elif words[0] == 'stack':
            self.display.print_stack(self)
        elif words[0] == 's':
            self.display.print_head(self)
        elif words[0] == 'setw':
            self.display.display_width = int(words[1])
        elif words[0] == 'p':
            self.stack.pop()
        elif words[0] == 'cm':
            self.cursor = self.parse_numeric(self.cursor, words[1])
            self.cursor = min(self.cursor, self.length())
            self.cursor = max(self.cursor, 0)
            self.display.print_head(self)
        elif words[0] == 'i':
            self.in_point = self.cursor
            self.display.print_head(self)
        elif words[0] == 'o':
            self.out_point = self.cursor
            self.display.print_head(self)
        elif words[0] == 'x':
            self.in_point = None
            self.out_point = None
            self.display.print_head(self)
        elif words[0] == 'k':
            self.crop_head()
        elif words[0] == 'd':
            pass
        elif words[0] == 'v':
            self.display.show_view_info(self)


        return True

    def run(self):
        self.display.print_stack(self)
        while True:
            command = self.get_input()
            if not self.handle_command(command):
                break


    
