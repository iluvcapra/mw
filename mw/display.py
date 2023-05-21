from mw.types import Milliseconds

from pydub import AudioSegment
from apeek import WaveformData, unicode_waveform

from typing import Optional

class Display:
    view_start: Milliseconds
    view_end:  Milliseconds
    display_width: int

    def __init__(self):
        self.display_width = 80
        self.view_start = 0
        self.view_end = 1

    def max_waveform_width(self) -> int:
        return self.display_width - 5
    
    def view_length(self):
        return self.view_end - self.view_start

    def print_width_for_length(self, length: Milliseconds) -> int:
        return int(self.max_waveform_width() * length / self.view_length())

    def create_sized_text_waveform(self, clip: AudioSegment, height: int) -> str:
        bins = self.print_width_for_length(len(clip))
        waveform = WaveformData.create_waveform_data(clip, time_bins=bins)
        return unicode_waveform(waveform.value_pairs, height=height)

    def print_frame(self, index, frame: 'StackFrame'):
        waveform_txt = self.create_sized_text_waveform(frame.clip(), height=2)
        print(waveform_txt.ljust(self.max_waveform_width()) + f" {index:02}")

    def print_frame_single(self, frame: 'StackFrame'):
        waveform_txt = self.create_sized_text_waveform(frame.clip(), height=6)
        print(waveform_txt)

    def print_stack(self, session: 'Session'):
        if len(session.stack) > 0:
            for i, frame in enumerate(reversed(session.stack[-3:])):
                self.print_frame(i, frame)
            print(f"Session length {session.length() / 1000.0} sec")
        else:
            print("Stack empty")

    def print_head(self, session: 'Session'):
        if len(session.stack) > 0:
            self.print_frame_single(session.stack[-1])
            self.print_ruler(session.cursor, session.in_point, session.out_point)
        else:
            print("Stack empty")

    def print_ruler(self, cursor: Milliseconds, in_point: Optional[Milliseconds], out_point: Optional[Milliseconds]):
        slug = list(" " * self.display_width)
        in_pos = None
        out_pos = None
        if in_point is not None:
            in_pos = self.print_width_for_length(in_point)
            slug[in_pos] = "["

        if out_point is not None:
            out_pos = self.print_width_for_length(out_point)
            slug[out_pos] = "]"

        if in_pos is not None and out_pos is not None:
            for i in range(in_pos + 1, out_pos):
                slug[i] = "⎯"

        slug[self.print_width_for_length(cursor)] = "^"
        print("".join(slug))

    def show_view_info(self, session: 'Session'):
        print(f"Display width: {self.display_width} cols")
        print(f"View start: {self.view_start} ms")
        print(f"View end: {self.view_end} ms")
        print(f"ms/col: {(self.view_end - self.view_start) // self.display_width}")



