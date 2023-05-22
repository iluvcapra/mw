from typing import Optional

import mw
from mw.types import Milliseconds

from pydub import AudioSegment
from apeek import WaveformData, unicode_waveform

class Display:
    # view_start: Milliseconds
    # view_end:  Milliseconds
    display_width: int

    def __init__(self):
        self.display_width = 80
        # self.view_start = Milliseconds(0)
        # self.view_end = Milliseconds(1)

    def max_waveform_width(self) -> int:
        return self.display_width - 5
    
    # def view_length(self) -> Milliseconds:
    #     return Milliseconds(self.view_end - self.view_start)

    def print_width_for_length(self, length: Milliseconds, view_length: Milliseconds) -> int:
        return int(self.max_waveform_width() * length / view_length )

    def create_sized_text_waveform(self, clip: AudioSegment, height: int, view_length: Optional[Milliseconds] = None) -> str:
        clip_view_length = Milliseconds(len(clip))
        if view_length is None:
            view_length = clip_view_length
        
        bins = self.print_width_for_length(clip_view_length, view_length)

        waveform = WaveformData.create_waveform_data(clip, time_bins=bins)
        return unicode_waveform(waveform.value_pairs, height=height)

    def print_frame(self, index, frame: 'mw.stack.StackFrame', session_length: Milliseconds):
        waveform_txt = self.create_sized_text_waveform(frame.clip(), height=2, view_length=session_length)
        print(waveform_txt.ljust(self.max_waveform_width()) + f" {index:02}")

    def print_frame_single(self, frame: 'mw.stack.StackFrame'):
        waveform_txt = self.create_sized_text_waveform(frame.clip_for_view(), height=6)
        print(waveform_txt)

    def print_stack(self, stack: 'mw.stack.Stack'):
        if len(stack.entries) > 0:
            session_length = stack.length()
            for i, frame in enumerate(reversed(stack.entries)):
                self.print_frame(i, frame, session_length)
            print(f"Session length {stack.length() / 1000.0} sec")
        else:
            print("Stack empty")

    def print_head(self, stack: 'mw.stack.Stack'):
        if stack.top:
            self.print_ruler(stack.top)
            self.print_frame_single(stack.top)
            self.print_selection(stack.top)
        else:
            print("Stack empty")
    
    def print_ruler(self, entry: 'mw.stack.StackFrame'):
        start_time = f"{entry.view_start}"
        end_time = f"{entry.view_end} ms"
        slug = list(" " * self.print_width_for_length(entry.view_length(),
                                                      entry.view_length()))

        slug[0:len(start_time)] = start_time
        slug[-len(end_time):] = end_time
        print("".join(slug))

    def print_selection(self, entry: 'mw.stack.StackFrame'):
        slug = list(" " * self.display_width)
        in_pos = None
        out_pos = None
        view_length = Milliseconds(len(entry.clip_for_view()))
        if entry.in_point is not None:
            in_pos = self.print_width_for_length(entry.in_point, view_length) 
            slug[in_pos] = "["

        if entry.out_point is not None:
            out_pos = self.print_width_for_length(entry.out_point, view_length)
            slug[out_pos] = "]"

        if in_pos is not None and out_pos is not None:
            for i in range(in_pos + 1, out_pos):
                slug[i] = "⎯"

        slug[self.print_width_for_length(entry.cursor, view_length)] = "⬆"
        print("".join(slug))

    def show_view_info(self):
        print(f"Display width: {self.display_width} cols")
        # print(f"View start: {self.view_start} ms")
        # print(f"View end: {self.view_end} ms")
        # print(f"ms/col: {(self.view_end - self.view_start) // self.display_width}")



