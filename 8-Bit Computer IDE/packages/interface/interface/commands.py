import sys
import re
from typing import Union

from .const import INTERFACE, CONN
from . import usercommand
from . import helptext


# Command functions to be used by the "UserCommand" class
# - Interface module automatically passes "self" to the function call.
#   use the methods from that instance for your operations.(input, log, etc...)
# - Returning nothing is assumed to be a success, if something goes wrong return
#   something else from the "const.INTERFACE", and/or call the "_error" from
#   the interface.
# - DON'T USE "print"! Use the "log" method of the interface.
# - For direct programmer commands, use "PR_*command*" naming scheme.
def _command_quit(interface:object) -> Union[int, None]:    
    if interface._quit_enable == True:
        sys.exit()
    else:
        interface.log("Quit command has been disabled!")

def _command_list_ports(interface:object) -> Union[int, None]:
    interface.log("Available ports:")
    for port in interface._serial_conn.serial_ports_list():
        interface.log(" > " + port)

def _command_help(interface:object) -> Union[int, None]:
    
    # If user gave more than 2 arguments
    if len(interface._input) > 2:
        interface.log("Invalid help command!")
        return
    
    # Is user typed "help" on its own
    if len(interface._input) == 1:
        interface.log(helptext.application)
        return
        
    # Is user typed "all"
    if interface._input[1] == "all":
        interface.log("Available commands: (use \"help *command*\" to get more info)")
        for command in commands:
            
            # Print the available inputs for each command(truncated or padded to be 25 characters)
            inputs_list = command.get_inputs_list()
            inputs_text = ""
            for i, input in enumerate(inputs_list):
                if i == 0:
                    inputs_text = f"-> \"{input}\""
                else:
                    inputs_text += f", \"{input}\""
            if len(inputs_text) > 22:
                inputs_text = inputs_text[:22] + "..."
            interface.log("{:<25}: ".format(inputs_text), end="")
            
            # Print the description for each command(truncated or padded to be 75 characters)
            description = re.search("Description: (.{1,75})(.|\n|$)", command.get_help())
            if description == None:
                interface.log("***Info missing!***")
            else:
                interface.log(description.group(1), end="")
                if len(description.group(1)) == 75:
                    interface.log("...")
                else:
                    interface.log('')
        return
    
    # If user gave 2 arguments(excluding "all")
    for command in commands:
        if command.check_command(interface._input[1]) == True:
            interface.log(command.get_help())
            return
        
    # Return command not found
    interface.log("Command not found!")
    return 
    
def _command_connect(interface:object) -> Union[int, None]:
    # User needs to give exactly 3 inputs
    if len(interface._input) != 3:
        interface.log("No valid input!")
        return
    
    # Connect to the given port with the given baud and start pinging
    interface.log(f"Trying to connect to port [{interface._input[1]}] with baud [{interface._input[2]}]!")
    try:
        interface._serial_conn.serial_start(interface._input[1], interface._input[2])
        if interface._ping_thread != None:
            interface._ping_thread.go()
        interface.log(f"Connection successful!")
    except Exception as err:
        interface.log(f"Connection failed! (Reason: {err})")
    
def _command_disconnect(interface:object) -> Union[int, None]:
    # Disconnect from the serial port if open
    status = interface._serial_conn.serial_status()
    if status[0] == False:
        interface.log("No connection to disconnect from!")
    else:
        if interface._ping_thread != None:
            interface._ping_thread.halt()
        interface._serial_conn.serial_stop()
        interface.log(f"Disconnected from port [{status[1]}] with baud [{status[2]}]!")
    
def _command_settings(interface:object) -> Union[int, None]:
    if len(interface._input) == 4:
        if interface._input[1] == "thread" and interface._input[2] == "verbose" and interface._input[3] == "1":
            interface._ping_thread.config(verbose=True)
            interface.log("Thread configured as verbose!")
            
        elif interface._input[1] == "thread" and interface._input[2] == "verbose" and interface._input[3] == "0":
            interface._ping_thread.config(verbose=False)
            interface.log("Thread configured as non-verbose!")
            
        else:
            interface.log("Invalid setting command!")       
    else:
        interface.log("Invalid setting command!")

def _command_connection_status(interface:object) -> Union[int, None]:
    # Print the status of the serial connection
    status = interface._serial_conn.serial_status()
    if status[0] == False:
        interface.log("Not connected!")
    else:
        interface.log(f"Connected to port [{status[1]}] with baud [{status[2]}]...")
           
def _command_PR_ping(interface:object) -> Union[int, None]:
    if interface._serial_conn.serial_status()[0] == False:
        interface.log("Not connected!")
        return
    
    interface._ping_thread.timer_reset()    
    try:
        response = interface._serial_conn.serial_send_packet(CONN.CMD_PING)
    except Exception:
        response = CONN.ERROR
        
    if response == CONN.STATUS_ACK:
        interface.log("Command successful!")    
    elif response == CONN.TIMEOUT:
        interface.log("Response timed out!")
    elif response == CONN.ERROR:
        interface.log("Failed to send packet!")
    else:
        interface.log("Invalid response!")
        
def _command_PR_reset(interface:object) -> Union[int, None]:
    pass


# List of commands available for the interface module
# - To add a command: create a function above and a help text in the helptext module
#   link them below using "UserCommand" class along with available inputs for the command.
# - If inputs overlap with another, only the command above will be executed.
commands = (
    usercommand.UserCommand(inputs=["q", "quit"]                 , func=_command_quit             , help=helptext.command_quit             ),
    usercommand.UserCommand(inputs=["lp", "list_ports"]          , func=_command_list_ports       , help=helptext.command_list_ports       ),
    usercommand.UserCommand(inputs=["h", "help"]                 , func=_command_help             , help=helptext.command_help             ),
    usercommand.UserCommand(inputs=["c", "connect"]              , func=_command_connect          , help=helptext.command_connect          ),
    usercommand.UserCommand(inputs=["d", "disconnect"]           , func=_command_disconnect       , help=helptext.command_disconnect       ),
    usercommand.UserCommand(inputs=["set", "setting", "settings"], func=_command_settings         , help=helptext.command_settings         ),
    usercommand.UserCommand(inputs=["s", "status"]               , func=_command_connection_status, help=helptext.command_connection_status),
    usercommand.UserCommand(inputs=["p", "ping"]                 , func=_command_PR_ping          , help=helptext.command_programmer_ping  ),
    usercommand.UserCommand(inputs=["r", "reset"]                , func=_command_PR_reset         , help=helptext.command_programmer_reset ),
)