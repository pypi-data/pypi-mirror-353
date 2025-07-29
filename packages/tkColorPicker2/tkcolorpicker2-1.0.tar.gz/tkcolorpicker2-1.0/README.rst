tkcolorpicker2
==============

|Release| |Windows| |Linux| |Mac| |License|

Color picker dialog for Tkinter. Forked from original https://github.com/j4321/tkColorPicker but with a locale fix.

This module contains a ``ColorPicker`` class which implements the color picker
and an ``askcolor`` function that displays the color picker and
returns the chosen color in RGB and HTML formats.


Requirements
------------

- Linux, Windows, Mac
- Python 2.7 or 3.x

And the python packages:

- tkinter (included in the python distribution for Windows)
- `Pillow <https://pypi.org/project/Pillow/>`_


Installation
------------

- With pip:

    ::

        $ pip install tkcolorpicker2


Documentation
-------------

Syntax:

::

    askcolor(color="red", parent=None, title=_("Color Chooser"), alpha=False)

Open a ColorPicker dialog and return the chosen color.

The selected color is returned as a tuple (RGB(A), #RRGGBB(AA))
(None, None) is returned if the color selection is cancelled.

Arguments:

    + color: initially selected color, supported formats:
    
        - RGB(A)
        - #RRGGBB(AA) 
        - tkinter color name (see http://wiki.tcl.tk/37701 for a list)
        
    + parent: parent window
    + title: dialog title
    + alpha: alpha channel suppport


Example
-------

.. code:: python

    import tkinter as tk
    import tkinter.ttk as ttk
    from tkcolorpicker import askcolor

    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use('clam')

    print(askcolor((255, 255, 0), root))
    root.mainloop()


.. |Release| image:: https://badge.fury.io/py/tkcolorpicker.svg
    :alt: Latest Release
    :target:  https://pypi.org/project/tkcolorpicker2/
.. |Linux| image:: https://img.shields.io/badge/platform-Linux-blue.svg
    :alt: Platform
.. |Windows| image:: https://img.shields.io/badge/platform-Windows-blue.svg
    :alt: Platform
.. |Mac| image:: https://img.shields.io/badge/platform-Mac-blue.svg
    :alt: Platform
.. |License| image:: https://img.shields.io/github/license/j4321/tkColorPicker.svg
    :target: https://www.gnu.org/licenses/gpl-3.0.en.html
    :alt: License
