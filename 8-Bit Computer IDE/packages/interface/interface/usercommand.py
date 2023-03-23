from typing import List, Callable


class UserCommand:
    def __init__(self, inputs:List[str], func:Callable, help:str) -> None:
        """Class used to define commands for the interface package.
        
            Methods:
            - check_comman()
            - execute()
            - get_help()
            - get_inputs_list()

        Args:
            inputs (List[str]): List of inputs for the command.
            func (Callable): Function to be called by the "execute" method.
            help (str): Help text for the command.
        """
        self._inputs = inputs
        self._func   = func
        self._help   = help
    
    def check_command(self, input:str) -> bool:
        """Returns "True" if the command matches, "False" otherwise."""
        if input in self._inputs:
            return True
        else:
            return False
    
    def execute(self, *args, **kwargs) -> int:
        """Executes the command's function with given arguments and returns its result."""
        return self._func(*args, **kwargs)
    
    def get_help(self) -> str:
        """Returns the help text of the command."""
        return self._help
    
    def get_inputs_list(self) -> List[str]:
        """Returns the inputs list for the command."""
        return self._inputs