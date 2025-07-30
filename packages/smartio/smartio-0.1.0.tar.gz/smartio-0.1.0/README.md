
# SmartIO

SmartIO is a smart, foolproof replacement for `print()` and `input()` that supports both console and Tkinter usage.

## Features
- Use `print_s()` and `input_s()` instead of `print()` and `input()`.
- Supports:
  - Console (default)
  - Tkinter widget objects (`Label`, `Text`, `Button`, `Entry`)
- Detects and raises errors if:
  - Wrong types are used.
  - Target widgets already have text.
  - Missing dependencies like `tkinter`.

## Usage

```python
import smartio

# Console
smartio.print_s("Hello!")
user_input = smartio.input_s("Enter your name:")

# Tkinter
import tkinter as tk
root = tk.Tk()
label = tk.Label(root)
label.pack()
entry = tk.Entry(root)
entry.pack()
button = tk.Button(root, text="Submit")
button.pack()

smartio.print_s("Hello from Tkinter!", source="tkinter", target=label)
name = smartio.input_s(source="tkinter", target=entry, enter_button=button)
```

## Requirements
- Python 3.x
- Tkinter (comes with standard Python installation)

## Licensing
You can choose from these permissive licenses depending on how you'd like to distribute:
- MIT License *(recommended for general open-source use)*
- Apache 2.0
- BSD 3-Clause

To officially distribute:
- Add a `LICENSE` file to your project directory.
- Include copyright.

No payment is required to use or apply these licenses.

## Author
Developed by [Your Name]. Contributions welcome!
