# xscreensaver-appearing-picture
Simple appearing picture screensaver for xscreensaver.

Demo at https://youtu.be/O3e0spl4ASo

# Features

* Simple installation and configuration
* Installed from repository

# Installation

## Archlinux
(Use Archlinux ARM for Raspberry install)

Add repository by adding this at end of file /etc/pacman.conf

```
[salamek]
Server = https://repository.salamek.cz/arch/pub/any
SigLevel = Optional
```

and then install by running

```bash
$ pacman -Sy xscreensaver-appearing-picture
```

# Debian and derivates

Add repository by running these commands

```bash
$ wget -O- https://repository.salamek.cz/deb/salamek.gpg | sudo tee /usr/share/keyrings/salamek-archive-keyring.gpg
$ echo "deb     [signed-by=/usr/share/keyrings/salamek-archive-keyring.gpg] https://repository.salamek.cz/deb/pub all main" | sudo tee /etc/apt/sources.list.d/salamek.cz.list
```

And then you can install a package `xscreensaver-appearing-picture`

```bash
$ apt update && apt install xscreensaver-appearing-picture
```

# Setup

After successful installation you will want to configure `xscreensaver` by editing `~/.xscreensaver` file adding this screensaver
or just delete your existing `~/.xscreensaver`, `xscreensaver-demo` will generate a new one.


# Usage:

```
$ xscreensaver-appearing-picture -h

Main entry-point into the 'xscreensaver-appearing-picture' application.
This is xscreensaver-appearing-picture.
License: GPL-3.0
Website: https://github.com/Salamek/xscreensaver-appearing-picture
Usage:
    xscreensaver-appearing-picture [--picture_path PICTURE_PATH] [--windowed] [--show_fps] [--animation_speed SPEED] [--fps FPS] [--background_color BACKGROUND_COLOR] [-window-id WINDOW_ID] [--display_time DISPLAY_TIME]
    xscreensaver-appearing-picture (-h | --help)
Options:
    -window-id WINDOW_ID                              Screensaver ID of window to run in.
    --windowed                                        Run in window.
    -f --show_fps                                     Show FPS.
    -c --picture_path PICTURE_PATH                    Screensaver path to picture to show.
    -t --display_time DISPLAY_TIME                    Display rendered image for number of seconds. [default: 5]
    -s --animation_speed SPEED                        Screensaver animation speed. [default: 1]
    -p --fps FPS                                      Screensaver FPS cap. [default: 30]
    -b --background_color BACKGROUND_COLOR            Screensaver background color. [default: #000000]
```