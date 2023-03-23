import sys
import threading

from .const import INTERFACE, CONN
from .      import commands
from .      import pingthread
from .      import customserial


class Interface:
    def __init__(self, output:object=sys.stdout, quit_enable:bool=True) -> None:
        """This class allows communication with the custom 8-bit computer programmer.
        - Will use the same command set, but multiple instances will work seperately as well.
        - Output set to "sys.stdout"(default) will use the main terminal for interfacing.
        - Implements "pingthread" which will ping the programmer when there hasn't been an active communication for a while.
        
            Methods:
            - command()
            - log()
            - set_output()
            - ping_start()
            - ping_thread_start()
            - ping_thread_stop()

        Args:
            output (object, optional): Output object whos "write" method will be called when printing. Defaults to sys.stdout.
            quit_enable (bool, optional): Enables or disables the "quit" command.(wouldnt' want interface to quit when using a gui or etc...) Defaults to True.
        """
        self._output      = output
        self._input       = ""
        self._quit_enable = quit_enable
        self._ping_thread = None
        self._serial_conn = customserial.CustomSerial()        
        self._lock        = threading.Lock()
        
    def command(self, input:str) -> None:
        """Takes a user input and finds a matching command, if found executes its function.

        Args:
            input (str): User input as a string.
        """
        # Skip if user only pressed enter
        if len(input) == 0:
            return
        else:
            self._input = input.lower().split()
    
        # Check for each command
        result = INTERFACE.CMD_NOTFOUND
        for command in commands.commands:
            if command.check_command(self._input[0]) == True:
                result = command.execute(self)
                break
            
        # Check for responses
        if result == INTERFACE.CMD_SUCCESS or result == None:
            pass
        elif result == INTERFACE.CMD_NOTFOUND:
            self.log("Invalid command! (Type \"help all\" to see the available commands.)")
        elif result == INTERFACE.CMD_CONN_ERROR:
            self._ping_thread.halt()
            self._serial_conn.serial_stop()
            self.log("Connection terminated!")
        
        # Log another newline before exiting
        self.log("")
        
    def log(self, msg:str, end:str='\n') -> None:
        """Mimics the built in "print" function but uses the interface output instead.
        - Thread safe.

        Args:
            msg (str): Message to print.
            end (str, optional): String to printed after the message. Defaults to '\n'.
        """
        with self._lock:
            self._output.write(msg)
            self._output.write(end)
        
    def set_output(self, output) -> None:
        """Changes the output.(The object whos "write()" method will be called for printing.)"""
        self._output = output
        
    def ping_thread_start(self):
        """Starts a new pingthread. Raises exceptions if one is already running."""
        if self._ping_thread != None:
            raise RuntimeError("Pingthread is already running!")
        self._ping_thread = pingthread.PingThread(interface=self, daemon=True)
        self._ping_thread.start()
                
    def ping_thread_stop(self):
        """Stops the ongoing pingthread. Raises exceptions the thread isn't running."""
        if self._ping_thread == None:
            raise RuntimeError("No running pingthread!")            
        self._ping_thread.stop()
        self._ping_thread = None
        
    def _error(self, error:int) -> None:
        """Handles the general error conditions.
        - Thread safe.

        Args:
            error (int): Constant from the "const.INTERFACE" class.
        """
        self._serial_conn.serial_stop()
            
        if error == INTERFACE.RESPONSE_TIMEOUT or error == INTERFACE.RESPONSE_INVALID:
            self.log("Programmer disconnected!")