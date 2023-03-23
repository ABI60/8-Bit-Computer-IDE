import threading
import time
import atexit

from .const import INTERFACE, CONN


class PingThread(threading.Thread):
    def __init__(self, *args, thread_name="", interface:object, **kwargs) -> None:
        """Subclass of "threading.Thread" made for the interface package. Pings the programmer periodically to keep a steady connection.
        - Ping command is sent every ~500ms, if ACK is not received, will automatically halt and call the "_error" method of the interface.
        - Initialized as halted
        - This thread doesn't need a "target" argument as the target function is implemented within the class.(you can directly call the "start()" method)
        - Requires "Interface" class as an argument, as the thread needs a "log" method along with access to the "serial" object.
        - Takes optional "name" argument if using multiple instances and distinguishing between them is required.
        - Optional arguments can be given to pass onto the "threading.Thread" superclass.
        
            Custom methods:
            - stop()
            - timer_reset()
            - halt()
            - go()
            - is_halted()
            - configure()

        Args:
            interface (object): Interface class object. Should be passed as "self" inside the class.
            thread_name (str, optional): Name of the thread for when configured as verbose. Defaults to "".
            *args, **kwargs: Other arguments for the "threading.Thread" superclass.
        """
        super().__init__(*args, target = self._ping_function, **kwargs)

        self._thread_name = thread_name        
        self._interface   = interface
        
        self._e_stop         = threading.Event()
        self._e_halt         = threading.Event()
        self._e_halt_changed = threading.Event()
        self._e_reset        = threading.Event()        
        self._e_verbose      = threading.Event()
        
        self._e_halt        .set()
        self._e_halt_changed.set()
        self._e_verbose     .set()
        
        self.config = self.configure
        atexit.register(self._termination_handler)

    def stop(self, timeout:int=3) -> None:
        """Sets the stop flag and waits for the thread to exit.
        - Blocks until exit or timeout

        Args:
            timeout (int, optional): Wait timeout in seconds. Defaults to 3.

        Raises:
            RuntimeError: RuntimeError: Raised on timeout.
        """
        self._e_stop.set()
        self.join(timeout=float(timeout))
        if self.is_alive() == True:
            raise RuntimeError("Failed to stop pingthread! -> " + str(threading.current_thread()))

    def timer_reset(self) -> None:
        """Resets the ping timer."""
        self._e_reset.set()

    def halt(self, timeout:int=3) -> None:
        """Sets the halt flag and waits for the thread to halt.
        - Blocks until halt or timeout

        Args:
            timeout (int, optional): Wait timeout in seconds. Defaults to 3.

        Raises:
            RuntimeError: RuntimeError: Raised on timeout.
        """
        if self._e_halt.is_set() == False:
            self._e_halt.set()     
            self._e_halt_changed.set()
            
            count = 0
            while(1):
                time.sleep(0.01)
                count += 1
                if self._e_halt_changed.is_set() == False:
                    break
                elif count > timeout*100:
                    raise RuntimeError("Failed to halt pingthread! -> " + str(threading.current_thread()))
        
    def go(self, timeout:int=3) -> None:
        """Sets the continue flag and waits for the thread to continue.
        - Blocks until continue or timeout

        Args:
            timeout (int, optional): Wait timeout in seconds. Defaults to 3.

        Raises:
            RuntimeError: RuntimeError: Raised on timeout.
        """
        if self._e_halt.is_set() == True:
            self._e_halt.clear()
            self._e_halt_changed.set()
            count = 0
            while(1):
                time.sleep(0.01)
                count += 1
                if self._e_halt_changed.is_set() == False:
                    break
                elif count > timeout*100:
                    raise RuntimeError("Failed to continue pingthread! -> " + str(threading.current_thread()))
            
    def is_halted(self) -> bool:
        """Returns the state of the halt flag."""
        return self._e_halt.is_set()

    def configure(self, verbose:bool=None) -> None:
        """Configures the pingthread.(options left empty(None) will remain unchanged)

        Args:
            verbose (bool, optional): "True" to enable verbose mode, "False" otherwise. Defaults to None.
        """
        if verbose == True:
            self._e_verbose.set()
        elif verbose == False:
            self._e_verbose.clear()
             
    def _vprint(self, msg:str) -> None:
        """Prints the message if the verbose mode is enabled.

        Args:
            msg (str): Message to print.
        """
        if self._e_verbose.is_set() == True:
            if self._thread_name == "":
                self._interface.log(f"***Pingthread: {msg}")
            else:
                self._interface.log(f"***Pingthread-{self._thread_name}: {msg}")
                
    def _termination_handler(self) -> None:
        """Exit handler to gracefully stop the thread."""
        # If the pingthread stops due to script end, it shouldn't print
        # to prevent errors due to output not existing(ex:tkinter apps)
        self._e_verbose.clear()
        self.stop()

    def _ping_function(self) -> None:
        """Thread function."""
        
        self._vprint("Starting thread!")
        
        # Loop time -> ~10ms | Timer -> ~500ms
        delay = 0.01
        TIMER = 50
        
        # Main loop
        counter = 0
        while(self._e_stop.is_set() == False):
            time.sleep(delay)
            
            # If halt state changed
            if self._e_halt_changed.is_set() == True:
                if self._e_halt.is_set() == True:
                    counter = 0
                    self._vprint("Thread halted!")
                else:
                    self._vprint("Thread continued!")
                self._e_halt_changed.clear()
            
            # If thread halted
            if self._e_halt.is_set() == True:
                continue
                    
            # If timer is reset
            if self._e_reset.is_set() == True:
                counter = 0
                self._e_reset.clear()
            else:
                counter += 1
                
            # If timer is due
            if counter == TIMER:
                counter = 0
                self._vprint("Pinging!")
                response = self._interface._serial_conn.serial_send_packet(CONN.CMD_PING)
                
                if response != CONN.STATUS_ACK:
                    self._vprint("Ping failed!")
                    self._e_halt.set()
                    self._e_halt_changed.set()
                    
                    if response == -1:
                        self._vprint("Response timed out!")
                        self._interface._error(INTERFACE.RESPONSE_TIMEOUT)
                    else:
                        self._vprint("Response invalid!")
                        self._interface._error(INTERFACE.RESPONSE_INVALID)
        
        # Pingthread exiting
        self._vprint("Exiting thread!")