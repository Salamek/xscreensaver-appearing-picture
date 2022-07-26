#!/usr/bin/env python3
"""Main entry-point into the 'xscreensaver-appearing-picture' application.
This is xscreensaver-appearing-picture.
License: GPL-3.0
Website: https://github.com/Salamek/xscreensaver-appearing-picture
Usage:
    xscreensaver-appearing-picture [--picture_path PICTURE_PATH] [--windowed] [--show_fps] [--animation_speed SPEED] [--fps FPS] [--background_color BACKGROUND_COLOR] [-window-id WINDOW_ID] [--display_time DISPLAY_TIME] [--alternative_loader]
    xscreensaver-appearing-picture (-h | --help)
Options:
    -window-id WINDOW_ID                              Screensaver ID of window to run in.
    --windowed                                        Run in window.
    -a --alternative_loader                              Use alternative picture loader instead of xscreensaver integrated one.
    -f --show_fps                                     Show FPS.
    -c --picture_path PICTURE_PATH                    Screensaver path to picture to show.
    -t --display_time DISPLAY_TIME                    Display rendered image for number of seconds. [default: 5]
    -s --animation_speed SPEED                        Screensaver animation speed. [default: 1]
    -p --fps FPS                                      Screensaver FPS cap. [default: 30]
    -b --background_color BACKGROUND_COLOR            Screensaver background color. [default: #000000]
"""
import datetime
import os
import signal
import sys
import subprocess
import shutil
import random

from pathlib import Path
from typing import List
from functools import wraps
from xscreensaver_config.ConfigParser import ConfigParser
from xscreensaver_appearing_picture.Screensaver import Screensaver
import xscreensaver_appearing_picture as app_root

from docopt import docopt

APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))

OPTIONS = docopt(__doc__)


def command(default: bool = False):
    def decorator(func):

        """Decorator that registers the chosen command/function.

        If a function is decorated with @command but that function name is not a valid "command" according to the docstring,
        a KeyError will be raised, since that's a bug in this script.

        If a user doesn't specify a valid command in their command line arguments, the above docopt(__doc__) line will print
        a short summary and call sys.exit() and stop up there.

        If a user specifies a valid command, but for some reason the developer did not register it, an AttributeError will
        raise, since it is a bug in this script.

        Finally, if a user specifies a valid command and it is registered with @command below, then that command is "chosen"
        by this decorator function, and set as the attribute `chosen`. It is then executed below in
        `if __name__ == '__main__':`.

        Doing this instead of using Flask-Script.

        Positional arguments:
        func -- the function to decorate
        """

        @wraps(func)
        def wrapped():
            return func()

        # Register chosen function.
        if func.__name__ not in OPTIONS and not default:
            raise KeyError('Cannot register {}, not mentioned in docstring/docopt that is not default.'.format(func.__name__))
        if func.__name__ in OPTIONS:
            command.chosen = func
        elif default:
            command.chosen = func

        return wrapped
    return decorator


class ImageResolver:
    _image_list = []
    _image_list_creation_time = None

    def _find_cat(self) -> str:
        cat_files = [f for f in [
            os.path.join('/', 'usr', 'share', 'xscreensaver-appearing-picture', 'cat.png'),
            os.path.abspath(os.path.join(APP_ROOT_FOLDER, '..', 'usr', 'share', 'xscreensaver-appearing-picture', 'cat.png')),
            os.path.join(APP_ROOT_FOLDER, '..', 'cat.png'),
        ] if os.path.exists(f)]

        if len(cat_files) == 0:
            raise ValueError('cat.png was not found in any search path')

        return cat_files[0]

    def _get_image_list(self, path: Path) -> List[Path]:
        if self._image_list_creation_time and self._image_list_creation_time + datetime.timedelta(seconds=60) < datetime.datetime.now():
            # Reset _image_list to force reload
            self._image_list = []

        if not self._image_list:
            for file in path.glob('*'):
                if file.is_file() and file.suffix.strip('.') in ['gif', 'jpeg', 'jpg', 'png', 'bmp']:
                    self._image_list.append(file)
            self._image_list_creation_time = datetime.datetime.now()

        return self._image_list

    def get_default_image(self) -> str:
        try:
            config_parser = ConfigParser(os.path.join(os.path.expanduser('~'), '.xscreensaver'))
            config_parsed = config_parser.read()

            image_directory_path = Path(config_parsed.get('imageDirectory'))
            if OPTIONS['--alternative_loader']:
                image_list = self._get_image_list(image_directory_path)
                if not image_list:
                    raise FileNotFoundError
                random_image_path = random.choice(image_list)
                if not random_image_path.is_file():
                    raise FileNotFoundError
                return str(random_image_path)

            found_xscreensaver_image_path = shutil.which('xscreensaver-getimage-file')
            if found_xscreensaver_image_path:
                random_image_name = subprocess.check_output(found_xscreensaver_image_path).decode('UTF-8').strip()
                random_image_path = image_directory_path.joinpath(random_image_name)
                if not random_image_path.is_file():
                    raise FileNotFoundError
                return str(random_image_path)
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

        return self._find_cat()


@command(default=True)
def run():
    image_resolver = ImageResolver()

    def picture_path_callable() -> Path:
        picture_path = Path(OPTIONS['--picture_path'] if OPTIONS['--picture_path'] else image_resolver.get_default_image())
        if not picture_path.is_file():
            raise ValueError('Path {} is not valid file.'.format(picture_path.absolute()))

        return picture_path

    Screensaver(
        picture_path_callable,
        not OPTIONS['--windowed'],
        OPTIONS['--show_fps'],
        animation_speed=int(OPTIONS['--animation_speed']),
        display_time=int(OPTIONS['--display_time']),
        fps=int(OPTIONS['--fps']),
        background_color=OPTIONS['--background_color'],
        window_id=OPTIONS['WINDOW_ID']
    ).run()


def main() -> None:
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))  # Properly handle Control+C
    getattr(command, 'chosen')()  # Execute the function specified by the user.


if __name__ == '__main__':
    main()
