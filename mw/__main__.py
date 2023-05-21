""" 
__main__.py

"""

import optparse

import pydub

from mw import __version__
from mw.stack import Stack

def main():
    print(f"mw v{__version__}")
    print(f"(c) 2023 Jamie Hardt. All Rights Reserved.", flush=True)
    parser = optparse.OptionParser()

    (options, files) = parser.parse_args()
    
    session = Stack(segments=[])

    for file in files:
        print(f"Reading audio file {file}...")
        audio = pydub.AudioSegment.from_file(file)
        session.push_sound(audio)
        
    
    session.run()


if __name__ == "__main__":
    main()
