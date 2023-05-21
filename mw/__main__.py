""" 
__main__.py

"""

import optparse

import pydub

from mw import __version__
from mw.app import App
from mw.types import Milliseconds

def main():
    print(f"mw v{__version__}")
    print(f"(c) 2023 Jamie Hardt. All Rights Reserved.", flush=True)
    parser = optparse.OptionParser()

    (_, files) = parser.parse_args()
    
    app = App()

    for file in files:
        print(f"Reading audio file {file}...")
        audio = pydub.AudioSegment.from_file(file)
        app.stack.push_sound(audio)
    
    # FIXME this is a bug
    app.display.view_start = Milliseconds(0)
    app.display.view_end = app.stack.length()
    
    app.run()


if __name__ == "__main__":
    main()
