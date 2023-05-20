from pydub import AudioSegment
from apeek import WaveformData, unicode_waveform

from typing import List


class StackFrame:
    segment: AudioSegment
    start: int
    end: int

    def __init__(self, segment: AudioSegment):
        self.segment = segment
        self.start = 0
        self.end = segment.frame_count()


class Session:
    stack: List[StackFrame]

    def __init__(self, segments : List[AudioSegment]):
        self.stack = []
        for segment in segments:
            self.stack.append(StackFrame(segment=segment))

    def print_frame(self, index, frame):
        waveform = WaveformData.create_waveform_data(frame.segment, time_bins=60)
        waveform_txt = unicode_waveform(waveform.value_pairs, height=1)
        print(f"{index:02} {waveform_txt}")

    def print_stack(self):
        for i, frame in reversed(list(enumerate(self.stack[0:3]))):
            if i == 0:
                self.print_frame(i, frame)
            else:
                self.print_frame(i, frame)

    def get_input(self):
        return input("> ")

    def handle_command(self, command):
        if command == 'q':
            return False
        return True

    def run(self):
        while True:
            self.print_stack()
            command = self.get_input()
            if not self.handle_command(command):
                break


    
