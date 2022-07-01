# -*- coding: utf-8 -*-

"""

"""
import os
import signal

import termcolor
from prompt_toolkit.shortcuts import yes_no_dialog, message_dialog
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

import pyfiglet

from i2c_lib.constants import (STYLES_GENERAL,
                               STYLES_ERROR,
                               STYLES_VALID,
                               TITLE)

def _report_log(message: str, type_log: str = "I") -> None:
    """Returns report log

    letter code to specify type of report

    'I' > Info | 'W' > Warning | 'E' > Error | 'S' > Success | 'V' > Verbose

    :Example:

    >>> _report_log("It seems your sentence is empty", "E")
    [ERROR   ⤬]  It seems your sentence is empty

    :param message: message to display in the log
    :type message: str
    :param type_log: type of message. Defaults to "I" (Info).
    :type type_log: str
    :return: None (print a log in defined color)
    :rtype: None
    """
    if type_log == "I":  # Info
        return print(f"[INFO    ℹ] {message}")
    if type_log == "W":  # Warning
        return termcolor.cprint(f"[WARNING ▲] {message}\n", "yellow")
    if type_log == "E":  # Error
        return termcolor.cprint(f"[ERROR   ⤬]  {message}\n", "red")
    if type_log == "S":  # Success
        return termcolor.cprint(f"[SUCCESS ✓]  {message}\n", "green")
    if type_log == "V":  # Verbose
        return termcolor.cprint(f"[DETAILS ℹ]  {message}\n", "blue")
    else:
        return print(message)


def generate_dialog(msg: str, type: str):
    style = STYLES_VALID
    if type == "E":
        style = STYLES_ERROR
    return message_dialog(
        title=TITLE,
        text=msg,
        style=Style.from_dict(style)).run()


def generate_yes_no_dialog(title: str, text: str):
    return yes_no_dialog(
        title=title,
        text=text,
        style=Style.from_dict(STYLES_GENERAL)).run()


def convert_to_html(text: str):
    return HTML(text)


def generate_figlet(msg: str, style: str, color: str):
    return termcolor.colored(pyfiglet.figlet_format(msg, font=style), color=color)

bottom_toolbar = HTML('<b>[x]</b> Abort Process.')

kb = KeyBindings()
cancel = [False]


@kb.add('x')
def _(event):
    " Send Abort (control-c) signal. "
    cancel[0] = True
    os.kill(os.getpid(), signal.SIGINT)




