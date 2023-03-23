import os
import math


from assembler_tools.assemblererror import *
from assembler_tools import mytokenizer
from assembler_tools import myparser
from assembler_tools.myparser import OPERATION_TYPE
from assembler_tools import mycodegenerator
from assembler_tools import hexops


def assemble(*, file: str, destination: str):
    """Assembles an asm file into a hex file.
    - Pass the paths as absolute for more information on syntax error.
    - Can raise normal file related errors(customized description)
    - ".hex" file is automatically removed on error.
    - Automatically adds the halt instruction at the end.
    - Max. number of instructions is 65535(2^16 - 1 due to the addition of halt at the end)
    
    Raises:
        SyntaxError: Syntax error is raised with custom description on assembly error so that
                     no custom exception needs to be included. Description contains 
                     description, row, colum, line information as a single string.

    Args:
        file (str): Destination for the asm file.(file extension needs to be given[.asm])
        destination (str): Destination for the hex file.(file extension needs to be given[.hex])
    """
    try:
        with open(file, 'r') as rf:
            with open(destination, 'w') as wf:                
                # Set the extended linear address to 0 before parsing
                hexops.write_record(wf, "04", data=[0x00, 0x00])
                
                # Pars each line
                instructions = []
                current_address = 0
                is_linear_address_one = False
                for i_line, line in enumerate(rf):
                    
                    # Tokenize the line, skip to next line if empty
                    tokens = mytokenizer.tokenize(line, i_line+1)
                    if tokens == []: continue
                    
                    # Parse the tokens
                    operation = myparser.pars(tokens)
                    operation_type, operation_args = operation
                    
                    
                    # Handle the operation
                    if operation_type == OPERATION_TYPE.MNEMONIC:
                        instructions.append(mycodegenerator.generate_instruction(operation_args))
                    else:
                        raise AssembleError("Invalid operation!", operation_args[0][1], operation_args[0][2], operation_args[0][3], operation_args[0][4])
                    
                    
                    # If the instructions reach 16-bytes(2*8-bytes:opcode/literal), create a record
                    # If address goes past 2-bytes, increment the extended linear address
                    if len(instructions) == 8:
                        data = []
                        for instruction in instructions:
                            data.append(instruction[0])
                            data.append(instruction[1])
                        hexops.write_record(wf, "00", current_address, data)
                        instructions = []
                        current_address += 16
                        if current_address == 0x10000:
                            if is_linear_address_one == True:
                                raise AssembleError("Instruction limit reached!(64kB)", operation_args[0][1], operation_args[0][2], operation_args[0][3], operation_args[0][4])
                            else:
                                is_linear_address_one = True
                                current_address = 0
                                hexops.write_record(wf, "04", data=[0x00, 0x01])
                
                # Add halt automatically at the end, along with leftover instructions
                data = []
                if len(instructions) > 0:
                    for instruction in instructions:
                        data.append(instruction[0])
                        data.append(instruction[1])
                halt_instruction = mycodegenerator.halt_instruction
                data.append(halt_instruction[0])
                data.append(halt_instruction[1])
                hexops.write_record(wf, "00", current_address, data)                    
                    
                # Write EOF before finishing
                hexops.write_record(wf, "01")
                
    except Exception as err:
        # If a hex file in the destination exists, remove it
        if os.path.isfile(destination) == True:
            os.remove(destination)
        
        # Handle the expected exceptions, if not expected, raise it again
        if isinstance(err, FileNotFoundError):   
            raise FileNotFoundError(f"No such file or directory:\n-> \"{file}\"") from None
        elif isinstance(err, OSError): 
            raise OSError(f"Invalid path:\n-> \"{err.filename}\"") from None
        elif isinstance(err, AssembleError):
            raise SyntaxError(f"Error in file \"{file}\", line: {err.row}, column: {err.column}\n"+
                              f"{err.description}: \"{err.value}\" -> {err.line}\n"+
                              " "*(len(err.description) + 7 + len(err.value) + err.column) + "^") from None
        else:
            raise err
       
       
def disassemble(*, file: str, destination: str, show_address=False, padding=35):
    """Disassembles a hex file into an asm file.
    - Can raise normal file related errors(customized description)
    - If record is flawed, may raise random errors
    - ".asm" file is automatically removed on error.
    
    Raises:
        SyntaxError: Syntax error is raised with custom description on disassembly error so that
                     no custom exception needs to be included.

    Args:
        file (str): Destination for the hex file.(file extension needs to be given[.hex])
        destination (str): Destination for the hex file.(file extension needs to be given[.asm])
        show_address (bool, optional): If True, will add address information for each instruction as comments(after the padding). Defaults to False.
        padding (int, optional): How many characters of padding to apply before the address comments(if True). All comments will line up to the
                                 padding; if the asm line spans longer than the padding, it will be clipped. Defaults to 35.
    """
    try:
        with open(file, 'r') as rf:
            with open(destination, 'w') as wf:
                
                # Check each record
                is_EOF_found = False
                is_extended_address_one = False
                for i_line, line in enumerate(rf):
                    
                    # Unpack the record
                    unpacked_record = hexops.unpack_record(line)
                    if unpacked_record == None:
                        raise DisassembleError("Invalid record!", i_line+1, line.replace("\n", ""))
                    else:                        
                        byte_count, address, record_type, data = unpacked_record
                        
                    # Check for start
                    if i_line==0:
                        if byte_count==2 and address==0 and record_type==4 and data[0][0] == 0 and data[0][1] == 0:
                            continue
                        else:
                            raise DisassembleError("Record start missing!", i_line+1, line.replace("\n", ""))
                        
                    # Check for extended linear address
                    if byte_count==2 and address==0 and record_type==4 and data[0][0] == 0 and data[0][1] == 1:
                        is_extended_address_one = True
                        continue
                        
                    # Check for EOF
                    if byte_count==0 and address==0 and record_type==1 and data==[]:
                        is_EOF_found = True
                        break
                    
                    # After here, every record should be data
                    if record_type != 0:
                        raise DisassembleError("Invalid record!", i_line+1, line.replace("\n", ""))
                        
                    # Disassemble data
                    for i_d, d in enumerate(data):
                        opcode, literal = d
                        asm = mycodegenerator.generate_assembly(opcode, literal)
                        if asm == None:
                            raise DisassembleError("Record doesn't match any instructions!", i_line+1, line.replace("\n", ""))
                        else:
                            if show_address == True:
                                if i_d == 0 and is_extended_address_one == True:
                                    address = address + 0x10000
                                true_address = math.floor(address/2)
                                comment = ";Address:" + "0x{0:04X}".format(true_address + i_d)
                                wf.write( "{0:<{1}}{2}\n".format(asm, padding, comment) )
                            else:
                                wf.write(f"{asm}\n")
                    
                # Raise exception if no EOF found
                if is_EOF_found == False:
                    raise DisassembleError("EOF(end of file) missing!",i_line+1, line.replace("\n", ""))  
                
    except Exception as err:
        # If a hex file in the destination exists, remove it
        if os.path.isfile(destination) == True:
            os.remove(destination)
        
        # Handle the expected exceptions, if not expected, raise it again
        if isinstance(err, FileNotFoundError):   
            raise FileNotFoundError(f"No such file or directory:\n-> \"{file}\"") from None
        elif isinstance(err, OSError): 
            raise OSError(f"Invalid path:\n-> \"{err.filename}\"") from None
        elif isinstance(err, DisassembleError):
            raise SyntaxError(f"Error in file \"{file}\", line: {err.row}\n"+
                              f"{err.description} -> {err.record}") from None
        else:
            raise err
       
       
def list_instructions():
    """Lists all available instrucion and their properties.
    - '*' denotes literal operand.

    Yields:
        Tuple[str, bool, str, int, int, int]: Instruction object -> (syntax, interchangeability, description, opcode, pipeline1, pipeline2)
    """
    # Construct the syntax and yield info for each instruction
    for instruction in mycodegenerator.instructions:
        syntax = f"{instruction.mnemonic}"
        for i, operand in enumerate(instruction.operands):
            if i==0:
                syntax += " "
            else:
                syntax += ", "
            syntax += operand
            
        yield (syntax, instruction.interchangeable, instruction.description, instruction.opcode, instruction.pip1, instruction.pip2)
           
            
def view(*, file: str, address_start, address_end=0, format='a'):
    """Returns the instruction(s) that reside in a given range of addresses  in a hex file.
    - "start_address" is inclusive while the "end_address" isn't
    - If no address end is given, will only return the given start address
    - Can raise normal file related errors(customized description)
    - If record is flawed, may raise random errors
    - Formats:(always returns strings, only changes the string itself)\n
     > 'a' ->  Instruction as assembly equivalent(disassembled)\n
     > 'h' ->  Instruction as opcode-literal pair(hex format)\n
     > 'b' ->  Instruction as opcode-literal pair(binary format)\n
     > 'd' ->  Instruction as opcode-literal pair(decimal format)\n
     
    Raises:
        SyntaxError: Syntax error is raised with custom description so that no custom exception
                     needs to be included.

    Args:
        file (str): Destination for the hex file.(file extension needs to be given[.hex])
        address_start (int): Start of the address.
        address_end (int, optional): End of the address. Defaults to 0.
        format (str, optional): Format of the return string. Defaults to 'a'.

    Returns:
        List(str): List of equivalent instructions for the given range.
    """
    
    try:
        with open(file, 'r') as rf:
                
                # Check each record
                is_extended_address_one = False
                return_list = []
                for line in rf:
                    
                    # Unpack the record
                    unpacked_record = hexops.unpack_record(line)
                    if unpacked_record == None:
                        continue
                    else:                        
                        byte_count, address, record_type, data = unpacked_record
                        
                    # Check for extended linear address
                    if byte_count==2 and address==0 and record_type==4 and data[0][0] == 0 and data[0][1] == 1:
                        is_extended_address_one = True
                        continue
                        
                    # Ignore non-data records
                    if record_type != 0:
                        continue
                        
                    # Calculate the real address and the end address for the record
                    if is_extended_address_one == True:
                        address += 0x10000
                    address = math.floor(address/2)
                    record_end = address+(byte_count/2)
                    
                    # Extract the data for the address and append to return list
                    while address_start >= address and address_start < record_end:
                        opcode, literal = data[address_start - address]      
                                          
                        if format == 'a':
                            asm = mycodegenerator.generate_assembly(opcode, literal)
                            if asm != None:
                                return_list.append(asm)
                            else:
                                raise ViewError("Opcode doesn't match any instructions!", address_start)
                        elif format == 'h':
                            return_list.append( "Opcode: 0x{0:02X}, Literal: 0x{1:02X}".format(opcode, literal) )
                        elif format == 'b':
                            return_list.append( "Opcode: 0b{0:08b}, Literal: 0b{1:08b}".format(opcode, literal) )
                        elif format == 'd':
                            return_list.append( "Opcode: {0:03}, Literal: {1:03}".format(opcode, literal) )
                        
                        # Go to next address; if reaches the end, return the list
                        address_start += 1
                        if address_start >= address_end:
                            return return_list
                
                # If no record left and didn't reach the end, raise error
                raise ViewError("Missing records for the range!", address_start)
                
    except Exception as err:        
        # Handle the expected exceptions, if not expected, raise it again
        if isinstance(err, FileNotFoundError):   
            raise FileNotFoundError(f"No such file or directory:\n-> \"{file}\"") from None
        elif isinstance(err, OSError): 
            raise OSError(f"Invalid path:\n-> \"{err.filename}\"") from None
        elif isinstance(err, ViewError):
            raise SyntaxError(f"Error in file \"{file}\"\n"+
                              f"{err.description} -> Address: {err.address}") from None
        else:
            raise err
            
            
            
assemble(file="packages//assembler//test.txt", destination="packages//assembler//test.hex")

# disassemble(file="packages//assembler//test.hex", destination="packages//assembler//disassembly.asm", show_address=True)


# assemble(file="packages//assembler//test2.txt", destination="packages//assembler//test.hex")

# result = view(file="packages//assembler//test.hex", address_start=0, address_end=5, format="a")
# for r in result:
#     print(r)



# ******************************************************************
    # make instructions read from file(make init function first)
    # make user interface code better
# ******************************************************************