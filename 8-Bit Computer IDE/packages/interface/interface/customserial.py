import serial
import serial.tools.list_ports
import threading
import time
import atexit
from typing import List, Union

from .const import CONN


class CustomSerial(serial.Serial):
    def __init__(self,  *args, **kwargs) -> None:
        """Subclass of "serial.Serial" made for the interface package.
        - "send_packet" method should be used instead of the "write" methods of the "serial.Serial" class.
        - All methods are thread safe.
        - Optional arguments can be given to pass onto the "serial.Serial" superclass.
        
            Custom Methods:
            - serial_start()
            - serial_stop()
            - serial_ports_list()
            - serial_send_packet()
            - serial_status()
            
        Args:
            *args, **kwargs: Other arguments for the "serial.Serial" superclass.
        """
        super().__init__(*args, **kwargs)
        self._serial_lock = threading.Lock()
        atexit.register(self._termination_handler)

    def serial_start(self, port:str, baud:str) -> None:
        """Opens a serial connection with the given port and baud rate.
        - Can raise exceptions if the port can't be opened or is already open.

        Args:
            port (str): Port to connect to.
            baud (str): Baud rate of the connection.
        """
        with self._serial_lock:
            self.port     = port
            self.baudrate = baud
            self.open()
    
    def serial_stop(self) -> None:
        """Closes the current connection.
        - Never raises exception.
        """
        with self._serial_lock:
            self.close()
    
    def serial_ports_list(self) -> List[str]:
        """Returns a list of all available COM ports."""
        with self._serial_lock:
            port_list = [str(port) for port in serial.tools.list_ports.comports()]
        return port_list

    def serial_send_packet(self, cmd:int, data_h:int=0, data_l:int=0) -> int:
        """Sends a 4-byte package with [command, data_high, data_low, checksum] format and returns the response.
        - Checksum is automatically calculated.
        - Response times out after ~10ms.
        - Can raise exceptions if the write operation can't be performed.

        Args:
            cmd (int): Command to be sent.
            data_h (int, optional): High 8-bits of the data to be sent. Defaults to 0.
            data_l (int, optional): Low 8-bits of the data to be sent. Defaults to 0.

        Returns:
            (int): Returns the response, "const.CONN.TIMEOUT" if times out.
        """
        # Calculate checksum(using 1's complement addition) & construct the package
        CKS = cmd + data_h + data_l
        CKS = (CKS >> 8) + (CKS & 0xFF)
        CKS = ~CKS & 0xFF
        packet = bytearray([cmd, data_h, data_l, CKS])
        
        # Thread protected write
        with self._serial_lock:
            self.reset_output_buffer()
            self.reset_input_buffer()
            self.write(packet)

            # Wait for a response
            for _ in range(10):
                if self.inWaiting() > 0:
                    return self.read()[0]
                time.sleep(0.001)
        
        # Timeout
        return CONN.TIMEOUT

    def serial_status(self) -> List[Union[bool, str, int]]:
        """Returns the status of the serial port along with the current port name and baudrate.

        Returns:
            (list(bool, str, int)): [Port status, port name, baudrate]
        """
        with self._serial_lock:
            status = [self.is_open, self.port, self.baudrate]
        return status
    
    def _termination_handler(self) -> None:
        """Exit handler to gracefully close the connection."""
        self.serial_stop()