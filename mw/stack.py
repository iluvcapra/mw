# from numpy import who
from pydub import AudioSegment
from pydub.playback import play

from mw.types import Milliseconds

from typing import List, Optional, cast 


class StackFrame: 
    segment: AudioSegment
    cursor: Milliseconds
    in_point: Optional[Milliseconds]
    out_point: Optional[Milliseconds]
    view_start: Milliseconds
    view_end: Milliseconds

    def __init__(self, segment: AudioSegment):
        self.segment = segment
        self.cursor = Milliseconds(0)
        self.in_point = None
        self.out_point = None
        self.view_start = Milliseconds(0)
        self.view_end = Milliseconds( len(segment) )

    def view_length(self) -> Milliseconds:
        assert self.view_end > self.view_start
        return Milliseconds( self.view_end - self.view_start )
    
    def zoom(self, factor: float):
        pass

    def crop(self, start: Milliseconds, end: Milliseconds):
        assert end > start, "crop end must be > crop start"
        self.segment = cast(AudioSegment, self.segment[start:end])
        self.in_point = None
        self.out_point = None
        self.cursor = Milliseconds(0)
        self.view_start = Milliseconds(0)
        self.view_end = Milliseconds(len(self.segment))

    def insert_silence(self, duration: Milliseconds, at: Milliseconds):
        assert at < len(self.segment), "Insertion point past end of sound"
        a = self.segment[0:at]
        b = self.segment[at:]
        silence = AudioSegment.silent(duration=duration)
        self.segment = a + silence + b
        self.view_start = Milliseconds(0)
        self.view_end = Milliseconds(len(self.segment))

    def bloop(self, duration: Milliseconds, at: Milliseconds):
        assert at + duration < len(self.segment)
        a = self.segment[0:at]
        b = self.segment[at + duration:]
        silence = AudioSegment.silent(duration)
        self.segment = a + silence + b

        self.view_start = Milliseconds(0)
        self.view_end = Milliseconds(len(self.segment))
    
    def fade_in(self, to: Milliseconds):
        assert (0 <= to < len(self.segment))
        self.segment = self.segment.fade_in(to)

    def fade_out(self, at: Milliseconds):
        assert (0 <= at < len(self.segment))
        self.segment = self.segment.fade_out(len(self.segment) - at)

    def clip_for_view(self) -> AudioSegment:
        return cast(AudioSegment, self.segment[self.view_start:self.view_end])

    def clip(self) -> AudioSegment:
        return self.segment

    def play(self):
        play(self.segment)

    def pad(self, to_length: Milliseconds):
        to_add = len(self.segment) - to_length
        if to_add > 0:
            self.segment = self.segment + AudioSegment.silent(to_add)

        self.view_start = Milliseconds(0)
        self.view_end = Milliseconds(len(self.segment))

    def export(self, filename):
        self.segment.export(filename,format='wav')


class Stack:
    entries: List[StackFrame]

    def __init__(self, segments : List[AudioSegment]):
        self.entries = []
        for segment in segments:
            self.push_sound(segment)
        
    @property
    def top(self) -> Optional[StackFrame]:
        """Get the top of the stack safetly."""
        if len(self.entries) > 0:
            return self.entries[-1]
        else:
            return None

    def push_sound(self, segment: AudioSegment):
        print(f"Pushing audio ({len(segment)} ms) onto stack...")
        self.entries.append(StackFrame(segment=segment))


    def split(self, at: Milliseconds):
        assert self.top is not None, "No sound on stack"
        to_split = self.top.segment
        a = cast(AudioSegment, to_split[0:at])
        b = cast(AudioSegment, to_split[at:])
        self.entries.pop()
        self.entries.append(StackFrame(a))
        self.entries.append(StackFrame(b))

   
    def append(self):
        assert len(self.entries) > 1

        a = self.entries.pop().segment
        b = self.entries.pop().segment
        self.entries.append(StackFrame(a + b))

        
    def prepend(self):
        assert len(self.entries) > 1

        a = self.entries.pop().segment
        b = self.entries.pop().segment
        self.entries.append(StackFrame(b + a))

    def loop(self, count: int = 2):
        assert len(self.entries) > 0
        a = self.entries.pop()
        segment = cast(AudioSegment, a.segment[a.in_point or 0:a.out_point or len(a.segment)])
        self.entries.append(StackFrame(segment * count))

    def bounce(self):
        assert len(self.entries) > 1
        
        a = self.entries[-1].segment
        b = self.entries[-2].segment

        if len(a) < len(b):
            a, b = b, a

        self.entries.pop()
        self.entries.pop()

        self.entries.append(StackFrame(a.overlay(b)))


    def length(self) -> Milliseconds:
        return Milliseconds(max(list(map(lambda x: len(x.clip()), self.entries)) + [0]))


