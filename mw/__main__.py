""" 
__main__.py

"""

import optparse

import pydub

from mw.session import Session

def main():
    parser = optparse.OptionParser()

    (options, files) = parser.parse_args()

    stack = []
    for file in files:
        audio = pydub.AudioSegment.from_file(file)
        stack.append(audio)

    session = Session(segments=stack)
    session.run()


if __name__ == "__main__":
    main()
