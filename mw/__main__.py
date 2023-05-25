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
    parser = optparse.OptionParser()
    parser.add_option("-e", "--exec", help="Execute command", 
                      action="append", metavar="COMMAND")
    (options, files) = parser.parse_args()
    
    app = App()
    
    print_banner()

    for file in files:
        print(f"Reading audio file {file}...")
        audio = pydub.AudioSegment.from_file(file)
        app.stack.push_sound(audio)
    
    for command in options.exec or []:
        app.handle_command_line(command)

    app.run()


if __name__ == "__main__":
    main()
