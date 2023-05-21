from pydub import AudioSegment
# from pydub.playback import play

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

    def crop(self, start: Milliseconds, end: Milliseconds):
        assert end > start, "crop end must be > crop start"
        self.segment = cast(AudioSegment, self.segment[start:end])
        self.in_point = None
        self.out_point = None
        self.cursor = Milliseconds(0)

    def crop_to_selection(self):
        self.crop(self.in_point or Milliseconds(0), 
                  self.out_point or Milliseconds(len(self.segment)))

    def insert_silence(self, duration: Milliseconds, at: Milliseconds):
        assert at < len(self.segment), "Insertion point past end of sound"
        a = self.segment[0:at]
        b = self.segment[at:]
        silence = AudioSegment.silent(duration=duration)
        self.segment = a + silence + b 
    
    def clip_for_view(self) -> AudioSegment:
        return cast(AudioSegment, self.segment[self.view_start:self.view_end])

    def clip(self) -> AudioSegment:
        return self.segment


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


    def split(self):
        if len(self.entries) > 0:
            to_split = self.entries[-1].segment
            a :AudioSegment = cast(AudioSegment, to_split[0:self.cursor])
            b :AudioSegment = cast(AudioSegment, to_split[self.cursor:])
            self.entries.pop()
            self.entries.append(StackFrame(a))
            self.entries.append(StackFrame(b))

        self.cursor = 0
        self.in_point = None
        self.out_point = None
        # self.display.view_start = 0
        # self.display.view_end = self.length()


    def length(self) -> Milliseconds:
        if len(self.entries) > 0:
            return Milliseconds(max(map(lambda x: len(x.clip()), self.entries)))
        else:
            return Milliseconds(0)
 
