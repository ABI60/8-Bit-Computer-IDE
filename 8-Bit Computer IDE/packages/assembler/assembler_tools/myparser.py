from typing import List

from .assemblererror import AssembleError
from .mytokenizer import TOKEN_TYPE


# Operation types for the detected parser operations
# - If more types are needed, add them ass a class variable with exclusive values
# 
# - New operations have to be assigned to the "operation_type" accordingly from the first token check below
# 
# - New operation grammers also need to be handled below
class OPERATION_TYPE:
    MNEMONIC = 0


def pars(tokens: List):
    """Returns the parsed operation and its arguments from the given list of tokens.
    - To use or see the possible opearations, type "from myparser import OPERATION_TYPE" and look at its variables

    Args:
        tokens (List[tokens]): Tokens list.

    Raises:
        AssembleError: Subclass of "Exception" with custom attributes -> (description, value, row, column, line)
        
    Returns:
        Tuple[OPERATION_TYPE, List[tokens]]: Tuple of the pars type and its arguments.(The first argument is always the OPERATION_TYPE's corresponding argument.)
    """
    # tokens -> [(token1)(token2)...]
    # token[0] -> type
    # token[1] -> value
    # token[2] -> row
    # token[3] -> column
    # token[4] -> line

    operation_type = None
    operation_args = []
    for i, token in enumerate(tokens):
        # Get the current and next token values
        type, value, row, column, line = token
        try:
            next_token = tokens[i+1]
            next_type, next_value, next_row, next_column, next_line = next_token
        except IndexError:
            next_type, next_value, next_row, next_column, next_line = (None, None, None, None, None)
                    
        # Check invalid tokens
        if i==0 and type == TOKEN_TYPE.INVALID:
            raise AssembleError("Invalid syntax!", value, row, column, line)
        if next_type != None and next_type == TOKEN_TYPE.INVALID:
            raise AssembleError("Invalid syntax!", next_value, next_row, next_column, next_line)
        
        # Check the first token seperately(determines the operation type)
        if i==0:
            if type == TOKEN_TYPE.ID:
                operation_type = OPERATION_TYPE.MNEMONIC
                operation_args.append(token)
            else:
                raise AssembleError("Invalid operation!", value, row, column, line)
            continue

        # -----------------------------AFTER OPERATION(AFTER FIRST TOKEN)-----------------------------

        # If the opearation is a mnemonic
        if operation_type == OPERATION_TYPE.MNEMONIC:
            
            if type == TOKEN_TYPE.ID or type == TOKEN_TYPE.LITERAL:
                if next_type == None or next_type == TOKEN_TYPE.SEPERATOR:
                    operation_args.append(token)
                else:
                    raise AssembleError("Expected seperator!", next_value, next_row, next_column, next_line)
                
            elif type == TOKEN_TYPE.SEPERATOR:
                if next_type == None:
                    raise AssembleError("Expected argument!", value, row, column, line)
                elif next_type == TOKEN_TYPE.ID or next_type == TOKEN_TYPE.LITERAL:
                    pass
                else:
                    raise AssembleError("Invalid argument!", next_value, next_row, next_column, next_line)
                
            else:
                raise AssembleError("Invalid argument!", next_value, next_row, next_column, next_line)
            
            
            
            
    # End of for loop for the tokens
    return (operation_type, operation_args)