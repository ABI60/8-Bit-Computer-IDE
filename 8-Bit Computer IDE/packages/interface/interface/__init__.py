"""
This is a custom module used to interface with the custom 8-bit computer programmer.

The package can be run directly to use the terminal as the interfacing tool by:
- calling the "interface.__main__.main()" method from a script
- running the package with "-m" from the terminal using python
- using the command "interface" directly on the terminal

---

To use the package in your project, create an "interface.Interface" instance and call
the "command" method with the users input.

Example:
    i = interface.Interface()
    while(1):
        i.command(input())

---

Multiple instances can be defined and used which will have their own pingthread and customserial.
However, they will still use the same command set.

Pingthread: custom thread class that will keep pinging the programmer in the background
to keep the connection alive.

Customserial: custom serial class that implements a 4-byte package communication method.

---

More commands can be added by going to the "commands.py" module and follow the instructions.
(No other part of the code should need changing unless something new needs implementing)

More communication constants can be added by going to the "const.py" module and defining them
under the "CONN" class.(may need other changes in other parts depending on the implementation)

"""
from .interface import Interface