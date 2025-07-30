"""
smartio.py - Smart Input and Output for Console and Tkinter

Author: Your Name (you can add your name and date here)
Version: 1.0

Purpose:
--------
This module provides enhanced input/output functionality for both the terminal (console)
and Tkinter GUIs using two main functions: `print_s()` and `input_s()`.

It is designed to:
- Replace `print()` and `input()` while being compatible with both CLI and Tkinter apps.
- Use direct widget references (not string IDs) for easier GUI programming.
- Avoid unnecessary complexity and third-party dependencies.

Supported Modes:
----------------
- Console (default): behaves like regular `print()` and `input()`.
- Tkinter:
    - Output: inserts text into a `Text` or `Entry` widget.
    - Input: fetches string from an `Entry` widget.
    - Requires the actual Tkinter widget to be passed via `element`.

Parameters Summary:
-------------------
All functions share these common optional arguments:
- source: 'console' (default) or 'tkinter'
- element: actual widget (like `tk.Text` or `tk.Entry`) for Tkinter mode
- detect_click / detect_enter: advisory flags that tell the function it's being called
  from a click or key event (not mandatory, but useful for coordination)

Example Usage:
--------------
# Console
print_s("Hello from CLI!")
name = input_s("What's your name? ")

# Tkinter
from tkinter import Tk, Text, Entry, Button

def on_submit():
    name = input_s(source="tkinter", element=entry, detect_click=True)
    print_s(f"Hello, {name}!", source="tkinter", element=output)

root = Tk()
output = Text(root)
output.pack()
entry = Entry(root)
entry.pack()
Button(root, text="Submit", command=on_submit).pack()
root.mainloop()
"""

import sys

def print_s(*args, source='console', element=None, detect_click=False, detect_enter=False, sep=' ', end='\n'):
    """
    Smart print function compatible with console and Tkinter.

    Parameters:
    - *args: Arguments to be printed (like the built-in print()).
    - source (str): 'console' (default) or 'tkinter'.
    - element: Required for Tkinter. A `tk.Text` or `tk.Entry` widget.
    - detect_click (bool): True if called by a button click (advisory).
    - detect_enter (bool): True if called on key press (advisory).
    - sep (str): Separator between arguments (default = ' ').
    - end (str): End character (default = '\n').

    Behavior:
    - Console: Prints to stdout.
    - Tkinter:
        - Text widget: Appends text at the end (only if empty).
        - Entry widget: Inserts text (only if empty).

    Raises:
    - ImportError: If Tkinter isn't available.
    - ValueError: If widget is invalid or missing.
    - RuntimeError: If widget already contains text.
    """
    text = sep.join(str(arg) for arg in args) + end

    if source == 'console' or source is None:
        print(text, end='')
        return

    elif source == 'tkinter':
        try:
            import tkinter as tk
        except ImportError:
            raise ImportError("Tkinter is not installed or not supported in this environment.")

        if element is None:
            raise ValueError("For Tkinter, you must pass the widget (Text or Entry) as 'element'.")

        if isinstance(element, tk.Text):
            existing = element.get("1.0", "end-1c")
            if existing.strip():
                raise RuntimeError("Text widget already has content.")
            element.insert("end", text)

        elif isinstance(element, tk.Entry):
            existing = element.get()
            if existing.strip():
                raise RuntimeError("Entry widget already has content.")
            element.insert("end", text)

        else:
            raise ValueError("Unsupported widget type. Use a Tkinter Text or Entry widget.")

        return

    else:
        raise ValueError(f"Unsupported source '{source}'. Use 'console' or 'tkinter'.")

def input_s(prompt=None, source='console', element=None, detect_click=False, detect_enter=False):
    """
    Smart input function compatible with console and Tkinter Entry.

    Parameters:
    - prompt (str): Prompt text for console input only.
    - source (str): 'console' (default) or 'tkinter'.
    - element: Required for Tkinter. A `tk.Entry` widget.
    - detect_click (bool): True if called by a button click (required for GUI flow).
    - detect_enter (bool): True if called on Enter key press (required for GUI flow).

    Returns:
    - str: The input value entered by the user.

    Behavior:
    - Console: Uses built-in input().
    - Tkinter: Returns content from Entry widget.

    Raises:
    - ImportError: If Tkinter isn't available.
    - ValueError: If widget is invalid or missing.
    - RuntimeError: If event detection flags are missing.
    """
    if source == 'console' or source is None:
        return input(prompt if prompt else '')

    elif source == 'tkinter':
        try:
            import tkinter as tk
        except ImportError:
            raise ImportError("Tkinter is not installed or not supported in this environment.")

        if element is None:
            raise ValueError("For Tkinter input, pass an Entry widget as 'element'.")

        if not hasattr(element, 'get'):
            raise ValueError("The provided widget must support a 'get()' method.")

        if not (detect_click or detect_enter):
            raise RuntimeError("Set detect_click=True or detect_enter=True to confirm user intent.")

        return element.get()

    else:
        raise ValueError(f"Unsupported source '{source}'. Use 'console' or 'tkinter'.")
