from pydub import AudioSegment
# from apeek import WaveformData, unicode_waveform

from mw.types import Milliseconds
from mw.display import Display
from mw.command_handler import CommandHandler

from typing import List, Optional 


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

    def length(self) -> Milliseconds:
        return max(map(lambda x: len(x.clip()), self.stack))

    def get_input(self):
        return input("> ")
    
    def handle_command(self, command):
        words = command.split()
        if words[0] == 'q':
            return False
        else:
            CommandHandler.handle(self, words)

        # elif words[0] == 'd':
        #     pass
        # elif words[0] == 'v':
        #     self.display.show_view_info(self)


        return True

    def run(self):
        self.display.print_stack(self)
        while True:
            command = self.get_input()
            if not self.handle_command(command):
                break


    
