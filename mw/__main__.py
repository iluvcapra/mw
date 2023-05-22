""" 
__main__.py

"""

import optparse

import pydub

from mw import __version__
from mw.app import App


def print_banner():
    print(f"mw {__version__}")
    print(f"(c) 2023 Jamie Hardt. All Rights Reserved.")


def main():
    print_banner()
    parser = optparse.OptionParser()
    (_, files) = parser.parse_args()
    
    app = App()

    for file in files:
        print(f"Reading audio file {file}...")
        audio = pydub.AudioSegment.from_file(file)
        app.stack.push_sound(audio)
    
    app.run()


if __name__ == "__main__":
    main()
