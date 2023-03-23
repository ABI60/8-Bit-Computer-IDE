class AssembleError(Exception):
    """Subclass of "Exception". Custom exception for the assembler errors.
    - Arguments explanation:\n
     >Description -> Description of the error\n
     >Value -> Value of where the error occured\n
     >Row -> Line row of where the error occured\n
     >Column -> Line column of where the error occured\n
     >Line -> The whole line of where the error occured\n
     >*args -> Other arguments for the "Exception" superclass.\n
     
    Args:
        Exception(str, str, int, int, str): (description, value, row, column, line, *args)
    """
    def __init__(self, description:str, value:str, row:int, column:int, line:str, *args):
        super().__init__(*args)
        self.description = description
        self.value       = value
        self.row         = row
        self.column      = column
        self.line        = line
        

class DisassembleError(Exception):
    """Subclass of "Exception". Custom exception for the assembler errors.
    - Arguments explanation:\n
     >Description -> Description of the error\n
     >Row -> Line row of where the error occured\n
     >Record -> Record of where the error occured\n
     
    Args:
        Exception(int, str): (row, record, *args)
    """
    def __init__(self, description:str, row:int, record:str, *args):
        super().__init__(*args)
        self.description = description
        self.row    = row
        self.record = record


class ViewError(Exception):
    """Subclass of "Exception". Custom exception for the assembler errors.
    - Arguments explanation:\n
     >Description -> Description of the error\n
     >Address -> Last adress of the error\n
     
    Args:
        Exception(str, int): (description, address, *args)
    """
    def __init__(self, description:str, address:int, *args):
        super().__init__(*args)
        self.description = description
        self.address = address