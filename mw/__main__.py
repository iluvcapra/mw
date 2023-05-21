""" 
__main__.py

"""

import optparse

import pydub

from mw import __version__
from mw.session import Session

def main():
    print(f"mw v{__version__}")
    print(f"(c) 2023 Jamie Hardt. All Rights Reserved")
    parser = optparse.OptionParser()

    (options, files) = parser.parse_args()
    
    session = Session(segments=[])

    for file in files:
        audio = pydub.AudioSegment.from_file(file)
        session.push_sound(audio)
        
    
    session.run()


if __name__ == "__main__":
    main()
