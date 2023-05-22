![](https://img.shields.io/github/license/iluvcapra/mw.svg) ![](https://img.shields.io/pypi/pyversions/mw.svg) [![](https://img.shields.io/pypi/v/mw.svg)](https://pypi.org/project/mw/) ![](https://img.shields.io/pypi/wheel/mw.svg)
[![Lint and Test](https://github.com/iluvcapra/mw/actions/workflows/python-package.yml/badge.svg)](https://github.com/iluvcapra/mw/actions/workflows/python-package.yml)

# mw

`mw` is an audio sample editor for the terminal. If you're ever in a terminal/tmux
session and just wanted to get a look at and maybe edit a sound file without
having to open a window, this is a tool for you!

# How to Use

Run `mw` from the command line with audio files as arguments. `mw` uses the pydub package
to read audio and supports any file format ffmpeg does.

```sh 
$ mw my_voice.wav robot_sounds.wav
```

File arguments are added to an internal stack and `mw` will present a command prompt. Most 
editing operations (like fadein, silence) act on the top-most sound on the stack. Some
commands `mw` supports include: _fadein, fadeout, silence, crop, bloop, split, bounce, 
export_. Each sound on the stack has an independent cursor, in- and out-point

For a complete list of commands, enter _help_ at the prompt.

# Screenshot

![Screenshot of an editing session](https://github.com/iluvcapra/mw/raw/master/docs/mw.png)

