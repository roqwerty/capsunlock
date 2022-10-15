'''
                                                                                   
                                       _____                                       
                                      / [_] \                                       
 _______ _______  _____  _______      |_____| __   _         _____  _______ _     _
 |       |_____| |_____] |______      |       | \  | |      |     | |       |____/ 
 |_____  |     | |       ______|      |_____| |  \_| |_____ |_____| |_____  |    \_


~~~ Reclaim your CapsLock! ~~~

CapsUnlock is an all-in-one keystroke and hotkey replacement engine to make Capslock into an actually useful key on the keyboard.
In addition, this provides modern upgrades and future-focused functionality that is at home in our world today.

Help text and hotkeys are printed when you run this program. They can also be found at the very end of this file.

---

Known Bugs:
    Windows keyboards that modify key locations when a modifier is pressed (like DVORAK w/QWERTY mappings) sometimes cannot
        read selected text (they default to reading from keyboard instead)
    CL+shift+q for making QR from clipboard passively causes inconsistent copying across keyboard layouts, and has been removed

Notes:
    The python math module is imported natively. When evaluating, type "sqrt(x)" instead of "math.sqrt(x)".
    An error in a hotkey will cause the caps lock event to no longer be overloaded. This means that if you selected malformatted
        python and try to run it, it *will* overwrite your selected python with the hotkey. Make backups, please.

Future plans:
    Run python/equations in their own threads to make the entire system more cohesive
    Runtime macro recording and replaying (options for key only & abs_mouse+key)
    More functionality for function graphing, like colors and axis titles and a legend
        3D plots?
    Read abbreviations from file and add the ability for runtime user to add their own.
    Conversion between decimal,binary,hex,ASCII,Base64,etc.
    GPT3 or GPT3-like integration?
    Mermaid-like image and flowchart generation from selected text to clipboard.
    Overlay window for useful data, like current clipboard contents.
        https://pythonprogramming.altervista.org/how-to-make-a-fully-transparent-window-with-pygame/
    Rendering and displaying LaTeX text like a QR code.
        https://stackoverflow.com/questions/1381741/converting-latex-code-to-images-or-other-displayble-format-with-python
    Checking eval for security exploits to make the entire system safer.
        https://stackoverflow.com/questions/32726992/how-to-plot-a-math-function-from-string
    Loading defaults and hotkeys and abbreviations from a comment at the end of this file, to keep the whole system as one script.
'''

from io import StringIO
from contextlib import redirect_stdout
import keyboard # Listening to keys. Doc: https://github.com/boppreh/keyboard
import pyperclip # Clipboard manipulation. Doc: https://pypi.org/project/pyperclip/
import pyautogui # Better keyboard hotkey sending
import matplotlib.pyplot as plt
import numpy as np
import multiprocessing
import easygui # popups and entering values
from math import *
import qrcode # qrcode feature

# Set up globals
if 'CLIPBOARD' not in globals():
    global CLIPBOARD
    CLIPBOARD = '' # The contents of the capsunlock-internal clipboard
if 'PAST_CLIPBOARDS' not in globals():
    global PAST_CLIPBOARDS
    PAST_CLIPBOARDS = [] # A list of all past capsunlock clipboards

# Gets and returns the selected text under the cursor from almost anywhere
def getSelectedText():
    # Store the current real clipboard, get text, and restock
    old_clip = pyperclip.paste()
    pyautogui.hotkey('ctrl', 'c') # This is a better hotkey system as it ignores existing held keys
    text = pyperclip.paste()
    pyperclip.copy(old_clip)
    return text

# Copies text to the internal clipboard
def clipboardCopy():
    global CLIPBOARD
    global PAST_CLIPBOARDS
    CLIPBOARD = getSelectedText()
    if CLIPBOARD != '':
        PAST_CLIPBOARDS.append(CLIPBOARD)

def clipboardCut():
    clipboardCopy()
    keyboard.press_and_release('\b')

def clipboardPaste():
    global CLIPBOARD
    keyboard.write(CLIPBOARD)

# Clipboard history popup wrapper
def clipboardHistoryWrapper(clipboards):
    text = easygui.choicebox("", 'CapsUnlock Clipboard History', clipboards)
    if text is not None:
        keyboard.write(text)

# Shows complete clipboard history and lets the user pick and paste one
def clipboardHistory():
    if len(PAST_CLIPBOARDS) >= 2: # Only display dialog if there are multiple opttions
        job = multiprocessing.Process(target=clipboardHistoryWrapper, args=(PAST_CLIPBOARDS,))
        job.start()
    else:
        clipboardPaste()

# Evaluates the selected expression and writes result. Depreciated
def evaluate():
    expression = getSelectedText()
    answer = eval(expression, globals())
    keyboard.send('right') # Deselect
    keyboard.write(' = ' + str(answer))

# Run the selected text as a python script and writes output in addition to anything else
def run():
    program = getSelectedText()
    keyboard.send('right') # Deselect
    s = '' # Output
    
    # Add print() around the last line so that things can be called like the interpreter (but only for one result at a time)
    lines = program.split('\n')
    lines[-1] = 'print(' + lines[-1] + ", end='')"
    program = '\n'.join(lines)
    # Run the program and redirect output
    f = StringIO()
    with redirect_stdout(f):
        exec(program, globals())
    s = f.getvalue()

    # If output is a single line, write it as a single line. Else, write as multiple lines
    if (len(s.split('\n')) == 1):
        keyboard.write(' = ' + s)
    else:
        keyboard.write('\n=\n' + s)

# Runs the selected text as a python script and writes output over the selected
def runover():
    program = getSelectedText()
    keyboard.send('\b') # Delete
    s = '' # Output
    
    # Add print() around the last line so that things can be called like the interpreter (but only for one result at a time)
    lines = program.split('\n')
    lines[-1] = 'print(' + lines[-1] + ", end='')"
    program = '\n'.join(lines)
    # Run the program and redirect output
    f = StringIO()
    with redirect_stdout(f):
        exec(program, globals())
    s = f.getvalue()

    keyboard.write(s)

# Multiprocessing function to graph a basic function
def showbasicplot(expl, lowerlimit, upperlimit, samples):
    # Graph each comma-separated function on the same plot
    exps = expl.split(';')
    plt.xlim(lowerlimit, upperlimit)
    for exp in exps:
        exp = exp.strip()
        print('Graphing f(x) = {}'.format(exp))
        x = np.linspace(lowerlimit, upperlimit, samples)
        def wrap(exp, globals, locals):
            try:
                return eval(exp, globals, locals)
            except:
                return None
        plt.plot(x, [wrap(exp, globals(), {'x': xi}) for xi in x])
    plt.show()

# Graphs the selected text with matplotlib
def graph():
    # Settings
    lowerlimit = -10
    upperlimit = 10
    samples = 1000

    # Actions
    exp = getSelectedText()
    exp = exp.replace('^', '**') # Make actual powers work in addition to python powers, as this is more accepted for graphing
    keyboard.send('right') # Deselect

    # Multiprocess show the graph
    job = multiprocessing.Process(target=showbasicplot, args=(exp, lowerlimit, upperlimit, samples))
    job.start()

# Graph the selected text expression(s) with more advanced parameters using a popup
def showadvplot(expl):
    # Get settings
    fields = ["Lower Limit (x)", "Upper Limit (x)", "Samples"]
    default_values = ['-10', '10', '1000']
    settings = easygui.multenterbox("Enter Advanced Graphing Options", "Graph Settings", fields, default_values)
    if settings == None or None in settings: # Empty or missing field, or cancel
        return

    # Use settings
    lowerlimit = float(settings[0])
    upperlimit = float(settings[1])
    samples = int(settings[2])

    # Graph each comma-separated function on the same plot
    showbasicplot(expl, lowerlimit, upperlimit, samples)

# Graphs the selected text with more advanced parameter popup
def advgraph():
    # Actions
    exp = getSelectedText()
    keyboard.send('right') # Deselect
    exp = exp.replace('^', '**') # Make actual powers work in addition to python powers, as this is more accepted for graphing

    # Multiprocess show the graph
    job = multiprocessing.Process(target=showadvplot, args=(exp,))
    job.start()

# Shows an image, new process compatible
def showImage(img, cmap):
    plt.axis('off')
    plt.imshow(img, cmap=cmap)
    plt.show()

# Makes and displays a QR code. Multiprocessable
def dispQR(text):
    qr = qrcode.QRCode()
    qr.add_data(text)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")
    img = np.logical_not(np.array(img)) # Binary image
    showImage(img, 'binary')

# Make a QR code of selected text and show
def qrify():
    # Actions
    text = getSelectedText()
    keyboard.send('right') # Deselect
    # Make and display QR through multiprocess
    job = multiprocessing.Process(target=dispQR, args=(text,))
    job.start()

# Make QR code from text in clipboard
'''
def qrifyclip():
    text = pyperclip.paste()
    job = multiprocessing.Process(target=dispQR, args=(text,))
    job.start()
'''



### DEV FUNCTIONS

# Scratch function, activated with +t
def scratch():
    print(getSelectedText())

# Utility function to read keypresses until 'esc' and print the names
def listen():
    print('Listening for keys to print their names.\nPress "esc" to stop.')
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            print(event.name)
            if event.name == 'esc':
                exit()

def nothing():
    pass

def main():
    # Set up the hotkeys
    #keyboard.add_hotkey('caps lock+esc', sys.exit, suppress=True) # Exit on Tab+Esc, but does not really work
    keyboard.add_hotkey('caps lock+t', scratch, suppress=True)
    # Block the caps lock key because who uses it anyway
    keyboard.block_key('caps lock')
    # Secondary clipboard
    keyboard.add_hotkey('caps lock+c', clipboardCopy, suppress=True)
    keyboard.add_hotkey('caps lock+x', clipboardCut, suppress=True)
    keyboard.add_hotkey('caps lock+v', clipboardPaste, suppress=True)
    keyboard.add_hotkey('caps lock+alt+v', clipboardHistory, suppress=True)
    # Evaluation
    keyboard.add_hotkey('caps lock+e', run, suppress=True)
    keyboard.add_hotkey('caps lock+r', runover, suppress=True) # Really doesn't like floating point numbers for some reason
    keyboard.add_hotkey('caps lock+g', graph, suppress=True)
    keyboard.add_hotkey('caps lock+shift+g', advgraph, suppress=True)
    # Visuals
    keyboard.add_hotkey('caps lock+q', qrify, suppress=True)
    #keyboard.add_hotkey('caps lock+shift+q', qrifyclip, suppress=True)
    # Navigation
    keyboard.add_hotkey('caps lock+i', keyboard.send, suppress=True, args=['up'])
    keyboard.add_hotkey('caps lock+j', keyboard.send, suppress=True, args=['left'])
    keyboard.add_hotkey('caps lock+k', keyboard.send, suppress=True, args=['down'])
    keyboard.add_hotkey('caps lock+l', keyboard.send, suppress=True, args=['right'])
    keyboard.add_hotkey('caps lock+shift+i', keyboard.send, suppress=True, args=['shift+up'])
    keyboard.add_hotkey('caps lock+shift+j', keyboard.send, suppress=True, args=['shift+left'])
    keyboard.add_hotkey('caps lock+shift+k', keyboard.send, suppress=True, args=['shift+down'])
    keyboard.add_hotkey('caps lock+shift+l', keyboard.send, suppress=True, args=['shift+right'])
    keyboard.add_hotkey('caps lock+ctrl+i', keyboard.send, suppress=True, args=['ctrl+up'])
    keyboard.add_hotkey('caps lock+ctrl+j', keyboard.send, suppress=True, args=['ctrl+left'])
    keyboard.add_hotkey('caps lock+ctrl+k', keyboard.send, suppress=True, args=['ctrl+down'])
    keyboard.add_hotkey('caps lock+ctrl+l', keyboard.send, suppress=True, args=['ctrl+right'])
    keyboard.add_hotkey('caps lock+ctrl+shift+i', keyboard.send, suppress=True, args=['ctrl+shift+up'])
    keyboard.add_hotkey('caps lock+ctrl+shift+j', keyboard.send, suppress=True, args=['ctrl+shift+left'])
    keyboard.add_hotkey('caps lock+ctrl+shift+k', keyboard.send, suppress=True, args=['ctrl+shift+down'])
    keyboard.add_hotkey('caps lock+ctrl+shift+l', keyboard.send, suppress=True, args=['ctrl+shift+right'])
    # Abbreviations
    #keyboard.add_abbreviation('@@', 'my.long.email@example.com')

    # Print help text
    print('''
    CapsUnlock 0.1

    (All below hotkeys are in ADDITION to the Caps Lock key)
    esc     : Exit CapsUnlock
    c/x/v   : Copy / Cut / Paste to a secondary clipboard
        +alt+v pastes anything from clipboard history (popup)
    e       : Evaluate selected text as math/python (unsecured)
    r       : Evaluate selected text as math/python AND REPLACE SELECTION (unsecured)
    i/j/k/l : Emulate the Arrow Keys (Also works with shift/ctrl)
    g       : Graph selected text as semicolon-separated f(x) equations
        +shift for additional graphing settings popup
    q       : Create and display a QR code for the selected text
        +shift to make from text in system keyboard (REMOVED)

    WIP:
    0-9     : Replay the macro recorded to the given digit
        +shift records a macro to the given digit, with overwriting
        +shift+alt records a macro with mouse events (absolute position)
    ''')

    # Do
    keyboard.wait('caps lock+esc')

if __name__ == '__main__':
    main()
