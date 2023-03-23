from tabnanny import check
from typing import List
   

def write_record(file, record_type: str, start_address=0, data=[]):
    """Writes a single hex record to the given file.
    - Calculates the byte count and checksum automatically.
    - If record type is 01(EOF-end of file) ignores the address and data.
    - If record type is 04(extended linear address) ignores address.
    - Other record types are not supported.
    
    - Shouldn't raise exceptions but writing can always fail.

    Args:
        file (file_object): File to write to.
        record_type (str): Record type.
        start_address (int, optional): Lower 2-byte address for the first data. Defaults to 0.
        data (List[int], optional): List of data to write(each data should be a single byte). Defaults to 0.
    """
    
    if record_type == "04":
        _write(file, 4, 0, data)
        
    elif record_type == "01":
        _write(file, 1, 0, [])
    
    elif record_type == "00":
        _write(file, 0, start_address, data)
        
        
def unpack_record(record):
    """Unpacks a line of record into its fields.
    - Validates checksum
    - Data is returned as opcode-literal tuple pair in a list.
    
    - Doesn't raise exceptions, instead returns "None"

    Args:
        record (str): Single line of record
        
    Returns:
        Tuple(int, int, int, List(Tuple(int, int)...)): Unpacked record -> (byte_count, address, record_type, (opcode, literal))
    """
    try:
        # Slice everything non-data
        byte_count  = int(record[1:3]  , 16)
        address     = int(record[3:7]  , 16)
        record_type = int(record[7:9]  , 16)
        checksum    = int(record[-3:-1], 16)    
        sum = byte_count + (address & 0xFF) + (address >> 8) + record_type
        
        # Save all data as opcode-literal typle pairs while calculating checksum
        data = []
        for i in range(0, byte_count*2, 4):
            opcode = int(record[i+9:i+11], 16)
            literal = int(record[i+11:i+13], 16)
            data.append((opcode, literal))
            sum += opcode + literal
        
        # Validate checksum
        if (sum+checksum) & 0xFF == 0:
            return (byte_count, address, record_type, data)
        else:
            return None
        
    except Exception:
        return None
    

def _write(file: object, record_type: int, address: int, data: List):
    # Calculate the checksum and bytecount(construct data hex string too)
    checksum = 0
    bytecount = 0
    data_str = ""
    for d in data:
        checksum += d
        bytecount += 1
        data_str += "{0:02X}".format(d)
        
    # Find the rest of the checksum
    checksum += bytecount + (address & 0xFF) + (address>>8) + record_type
    checksum = (~checksum + 1) & 0xFF
    
    # Construct the rest of the hex strings
    bytecount_str = "{0:02X}".format(bytecount)
    address_str = "{0:04X}".format(address)
    recor_type_str = "{0:02X}".format(record_type)
    checksum_str = "{0:02X}".format(checksum)
    
    # Write the record
    file.write(":" + bytecount_str + address_str + recor_type_str + data_str + checksum_str + "\n")