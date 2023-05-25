![](https://img.shields.io/github/license/iluvcapra/mw.svg) ![](https://img.shields.io/pypi/pyversions/mw.svg) [![](https://img.shields.io/pypi/v/mw.svg)](https://pypi.org/project/mw/) ![](https://img.shields.io/pypi/wheel/mw.svg)
[![Lint and Test](https://github.com/iluvcapra/mw/actions/workflows/python-package.yml/badge.svg)](https://github.com/iluvcapra/mw/actions/workflows/python-package.yml)

# mw

`mw` is an interactive, text-mode audio sample editor. Audio files provided as arguments
on the command line can be inspected, edited, mixed and exported.

If you're ever in a terminal/tmux session and just wanted to get a look at and maybe edit 
a sound file without having to open a window, this is a tool for you!

# How to Use

Run `mw` from the command line with audio files as arguments. `mw` uses the pydub package
to read audio and supports any file format ffmpeg does.

```sh 
$ mw my_voice.wav robot_sounds.wav
```

File arguments are added to an internal stack and `mw` will present a command prompt. Some
commands `mw` supports include: _fadein, fadeout, silence, crop, bloop, split, bounce,_ and
_export_.

For a complete list of commands, enter _help_ at the prompt or read `mw`'s manpage.

# Screenshot

![Screenshot of an editing session](https://github.com/iluvcapra/mw/raw/master/docs/mw.png)

