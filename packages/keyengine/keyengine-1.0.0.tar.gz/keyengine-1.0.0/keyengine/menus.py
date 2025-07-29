from . import keydetection as kd
import colorama
import time
import os
import sys
import keyboard

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    try:
        from deprecated import deprecated
    except ImportError:
        raise ImportError("ImportError: Please import the `deprecated` library unless you have Python 3.13 or newer. If you have Python 3.13 or newer and are seeing this, please open an issue on Github.")

clear = lambda: os.system('cls || clear')

@deprecated('This function was depreacted in v1.0.0. Please use the new menu() function instead, as this one has many errors/issues.')
def plain_menu(choices: list[str]):
    global clear
    c = 0
    if c == -1: c = 6
    if c == 7: c = 0
    for option in choices:
        if choices[c] == option:
            print(f"{colorama.Style.BRIGHT}{option} <{colorama.Style.RESET_ALL}")
        else:
            print(option)
    while kd.current_key != 'enter':
        time.sleep(0.08)
        if kd.current_key != '':
            clear()
            if kd.current_key == 'up':
                c -= 1
            if kd.current_key == 'down':
                c += 1
            if c == -1: c = 6
            if c == 7: c = 0
            for option in choices:
                if choices[c] == option:
                    print(f"{colorama.Style.BRIGHT}{option} <{colorama.Style.RESET_ALL}")
                else:
                    print(option)

    flush_stdin()

    return c

def flush_stdin():
    """
    Flush any unread input from sys.stdin so that the leftover ENTER
    doesn’t immediately satisfy the next input() call.
    """
    try:
        # Unix‐style flush
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except (ImportError, OSError):
        # Windows‐style flush
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()

def menu(choices: list[str], index: bool = True):
    global clear

    def with_index(thing):
        nonlocal index
        if not index: return thing
        return str(choices.index(thing)) + '. ' + thing

    c = 0
    if c == -1: c = len(choices) - 1
    if c == len(choices): c = 0
    for option in choices:
        if choices[c] == option:
            print(f"{colorama.Style.BRIGHT}{option} <{colorama.Style.RESET_ALL}")
        else:
            print(option)
    kd.start_input(True)
    while not keyboard.is_pressed('enter'):
        time.sleep(0.06)
        search = kd.INPUT
        if kd.current_key != '':
            clear()
            if keyboard.is_pressed('up'):
                c -= 1
                if c == -1: c = len(choices) - 1
                if c == len(choices): c = 0
                i = 0
                while not choices[c].startswith(search) or with_index(choices[c]).startswith(search):
                    i += 1
                    c += -1
                    if c == -1: c = len(choices) - 1
                    if c == len(choices): c = 0
                    if i >= len(choices):
                        search = search[:-1]
                        i = 0
            if keyboard.is_pressed('down'):
                c += 1
                if c == -1: c = len(choices) - 1
                if c == len(choices): c = 0
                i = 0
                while not choices[c].startswith(search) or with_index(choices[c]).startswith(search):
                    i += 1
                    c += 1
                    if c == -1: c = len(choices) - 1
                    if c == len(choices): c = 0
                    if i >= len(choices):
                        search = search[:-1]
                        i = 0

            if c == -1: c = len(choices) - 1
            if c == len(choices): c = 0
            for option in choices:
                if not (choices[c] == option or option.startswith(search) or with_index(option).startswith(search)):
                    continue
                if choices[c] == option:
                    print(f"{colorama.Style.BRIGHT}{option} <{colorama.Style.RESET_ALL}")
                else:
                    print(option)
            sys.stdout.write(f'------\n{kd.INPUT}')

    flush_stdin()

    return c

