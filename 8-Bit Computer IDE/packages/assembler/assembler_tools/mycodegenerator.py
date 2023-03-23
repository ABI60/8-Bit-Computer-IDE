from typing import List, Union
import copy

from .assemblererror import AssembleError
from .mytokenizer import TOKEN_TYPE


# Check page: https://docs.python.org/3/library/copy.html
# for information about the "copy.deepcopy()" usage


class Instruction:
    """Class for generating new instructions.
    - Each instruction must have:
     >opcode          -> 8-bit opcode for the instruction\n
     >pip1            -> 8-bit value for the pipeline-1 decoder\n
     >pip2            -> 8-bit value for the pipeline-2 decoder\n
     >mnemonic        -> mnemonic value for the instruction(case sensitive)\n
     >operands        -> list of operands for the mnemonic(case sensitive)(empty list if no operands)('*' denotes literal)\n
     >interchangeable -> "True" if the order of the operands don't matter, "False" otherwise \n
     >description     -> Description of the instruction\n
    """
    def __init__(self, *, opcode: int, pip1: int, pip2: int, mnemonic: str, operands: Union[List[str], None], interchangeable: bool, description: str):
        self.opcode          = opcode
        self.pip1            = pip1
        self.pip2            = pip2
        self.mnemonic        = mnemonic
        self.operands        = operands
        self.interchangeable = interchangeable
        self.description     = description


# Instruction list containing all defined instructions
# - If more instructions are needed, add them them below using the "Instruction" class
# 
# - Read the class doc for the description of the inputs.
# 
# - '*' symbol denotes literal operand. Only 1 literal is allowed; even if you put 2 '*'s, they won't be checked,
#   since the generator detects if there are more than 1 literal arguments in the asm file input and throws an error.  
# 
# - Other operands should be text of '_' only, as the tokenizer will assume everything else to be invalid; they also can't
#   contain spaces, '-' etc...(make sure they are text or '_' only)
# 
# - Other operands will be checked whether they are the exact same as the input from the asm file or not. If the
#   opcode is the same for more than 1 mnemonic-operand(wihtout interchangeability) you can define them
#   seperately and give them the same opcode.
# 
# - There can be multiple instructions with the same mnemonic but make sure their operands are different.
# 
# - If you make a mistake and more than 1 instruction matches the asm file input, the first match in the list will
#   be returned, so the script won't break.
instructions = (
    ( Instruction(opcode=0x00, pip1=0x00, pip2=0x00, mnemonic="nop" , operands=[]             , interchangeable=False, description="No operation.")                       ),
    ( Instruction(opcode=0x01, pip1=0x00, pip2=0x00, mnemonic="halt", operands=[]             , interchangeable=False, description="Halts the computer.")                 ),
    ( Instruction(opcode=0x02, pip1=0x00, pip2=0x00, mnemonic="mov" , operands=["*", "a"]     , interchangeable=False, description="Move literal to A-register.")         ),
    ( Instruction(opcode=0x03, pip1=0x00, pip2=0x00, mnemonic="mov" , operands=["*", "b"]     , interchangeable=False, description="Move literal to B-register.")         ),
    ( Instruction(opcode=0x04, pip1=0x00, pip2=0x00, mnemonic="mov" , operands=["a", "b"]     , interchangeable=False, description="Move A-register to B-register.")      ),
    ( Instruction(opcode=0x05, pip1=0x00, pip2=0x00, mnemonic="mov" , operands=["b", "a"]     , interchangeable=False, description="Move B-register to A-register.")      ),
    ( Instruction(opcode=0x06, pip1=0x00, pip2=0x00, mnemonic="mov" , operands=["result", "a"], interchangeable=False, description="Move result-register to A-register.") ),
    ( Instruction(opcode=0x07, pip1=0x00, pip2=0x00, mnemonic="mov" , operands=["result", "b"], interchangeable=False, description="Move result-register to B-register.") ),
    ( Instruction(opcode=0x08, pip1=0x00, pip2=0x00, mnemonic="add" , operands=["a", "b"]     , interchangeable=True , description="Add A-register and B-register.")      ),
)

# Opcode-literal for the halt instruction
halt_instruction = (0x01, 0)


def generate_instruction(operation_args):
    """Generates the matching instruction-literal pair for the given parser arguments.

    Args:
        operation_args (List[tokens]): Parser output arguments.

    Raises:
        AssembleError: Subclass of "Exception" with custom attributes -> (description, value, row, column, line)

    Returns:
        Typle[opcode, literal]: Return the 8-bit matching instruction opcode and the given literal(0 if none given).
    """
    # First token cantains the mnemonic, while the rest are arguments
    # operation_args -> [(token1)(token2)...]
    # token[0] -> type
    # token[1] -> value
    # token[2] -> row
    # token[3] -> column
    # token[4] -> line
    
    
    # Unpack all of the information(first argument contains the mnemonic token)
    mnemonic_arg = operation_args[0] 
    other_args   = operation_args[1:]
    mnemonic_type, mnemonic_value, mnemonic_row, mnemonic_column, mnemonic_line = mnemonic_arg
    
    
    # Group all instructions who's mnemonics match
    # Raise error if there are no matches
    possible_instructions = [copy.deepcopy(i) for i in instructions if i.mnemonic == mnemonic_value]
    if len(possible_instructions) == 0:
        raise AssembleError("Unknown mnemonic!", mnemonic_value, mnemonic_row, mnemonic_column, mnemonic_line)
    
    
    # Find the minimum and maximum operand count for the mnemonic
    # Raise error if the line has too many or too few arguments
    operand_lengths = [len(i.operands) for i in possible_instructions]
    min_arg = min(operand_lengths)
    max_arg = max(operand_lengths)
    if len(other_args) > max_arg:
        raise AssembleError("Too many arguments!", mnemonic_value, mnemonic_row, mnemonic_column, mnemonic_line)
    if len(other_args) < min_arg:
        raise AssembleError("Missing arguments!", mnemonic_value, mnemonic_row, mnemonic_column, mnemonic_line)
    
    
    # Remove instructions that don't match the argument count
    # Raise error if no instructions left
    temp = possible_instructions.copy()
    possible_instructions = [i for i in temp if len(i.operands) == len(other_args)]
    if len(possible_instructions) == 0:
        raise AssembleError("Mnemonic doesn't match arguments!", mnemonic_value, mnemonic_row, mnemonic_column, mnemonic_line)
    
    
    # Find all literal arguments; if no errors, get the literal value
    # Raise error if there are more than one (with the last literal argument)
    literal_count = 0
    literal = 0
    for arg in other_args:
        if arg[0] == TOKEN_TYPE.LITERAL:
            literal_count += 1
            _, literal_value, literal_row, literal_column, literal_line = arg
            literal = int(literal_value)
    if literal_count > 1:
        raise AssembleError("Too many literals!", literal_value, literal_row, literal_column, literal_line)
    elif literal > 255:
        raise AssembleError("Literal can't be more than 255!", literal_value, literal_row, literal_column, literal_line)
    
    
    # ********************************************************************
    # After here:
    # - At least 1 instruction matched the mnemonic
    # - Matched instruction(s) have the same argument count as the "other_args"
    # - "other_args" doesn't have more than 1 literal (can still have none)
    # -------------------------------------------------------------------
    # "possible_instructions" contains the instructions that matched
    # "other_args" contains the line arguments
    # "literal" contains the literal's integer value (default 0 if no literal)
    # ********************************************************************
    
    
    # Find the matching instructions by checking each argument with their corresponding operand
    for i_arg, arg in enumerate(other_args):
        arg_type, arg_value, arg_row, arg_column, arg_line = arg
        
        for i_inst, instruction in enumerate(possible_instructions):
            
            # Set the instructions that don't match the argument to "None"
            # If interchangeable, remove that argument for the future checks
            if instruction.interchangeable == False:
                operand = instruction.operands[i_arg]
                if arg_type == TOKEN_TYPE.ID and arg_value == operand:
                    pass
                elif arg_type == TOKEN_TYPE.LITERAL and "*" == operand:
                    pass
                else:
                    possible_instructions[i_inst] = None
            else:
                if arg_type == TOKEN_TYPE.ID and arg_value in instruction.operands:
                    instruction.operands.remove(arg_value)
                elif arg_type == TOKEN_TYPE.LITERAL and "*" in instruction.operands:
                    instruction.operands.remove("*")
                else:
                    possible_instructions[i_inst] = None
    
        # Remove the "None" instructions
        # If nothing left, raise error with the current arguments
        temp = possible_instructions.copy()
        possible_instructions = [i for i in temp if i != None]
        if len(possible_instructions) == 0:
            raise AssembleError("Invalid argument!", arg_value, arg_row, arg_column, arg_line)
    
            
    # If there is an instruction left, send the first one with the literal
    # If more than 1 instruction fits the bill, still send the first match
    return (possible_instructions[0].opcode, literal)






def generate_assembly(opcode, literal):
    """Generates the matching asm line for the given opcode-literal pair.
    
    - Doesn't raise exceptions, instead returns "None" if no instruction matches 

    Args:
        opcode (int): Opcode of the instruction
        literal (int): Literal of the instruction

    Returns:
        str: Asm line equivalent constructed as a list(doesn't contain newline at the end)
    """
    # Check each instruction for an opcode match
    return_string = ""
    is_instruction_found = False
    for instruction in instructions:
        
        # If instruction matches, add it to the string
        if opcode == instruction.opcode:
            is_instruction_found = True
            return_string += instruction.mnemonic
            
            # Add each operand(only add the literal if it exists as an operand)
            for i, operand in enumerate(instruction.operands):
                if i==0:
                    return_string += " "
                else:
                    return_string += ", "
                    
                if operand == "*":
                    return_string += str(literal)
                else:
                    return_string += operand
          
    # Return the result asm line
    if is_instruction_found == True:
        return return_string      
    else:
        return None