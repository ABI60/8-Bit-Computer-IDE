# Constant classes should not be mixed together. They should be used in
# their intended contexts to avoid overlapping.


class INTERFACE:
    """General package constants."""
    RESPONSE_TIMEOUT = 0
    RESPONSE_INVALID = 1
    
    CMD_SUCCESS    = 2
    CMD_NOTFOUND   = 3
    CMD_CONN_ERROR = 4
    
    
class CONN:
    """Communication related constants."""
    CMD_PING         = 0x01
    CMD_RESTART      = 0x02
    CMD_MODE_24      = 0x03
    CMD_MODE_40      = 0x04
    CMD_MODE         = 0x05
    CMD_MODE_PROGRAM = 0x06
    CMD_RESET        = 0x07
    CMD_RESET_HOLD   = 0x08
    CMD_HALT         = 0x09
    CMD_RELEASE      = 0x0A
    CMD_CLOCK        = 0x0B
    CMD_CLOCK_RAISE  = 0x0C
    CMD_CLOCK_FALL   = 0x0D
    CMD_PC_ENABLE    = 0x0E
    CMD_PC_DISABLE   = 0x0F

    TIMEOUT             = -2
    ERROR               = -1
    STATUS_ACK          = 0xFF
    STATUS_NACK         = 0x00
    STATUS_MODE_24      = 0x0F
    STATUS_MODE_40      = 0xF0
    STATUS_MODE_STANDBY = 0xCC
    STATUS_MODE_PROGRAM = 0x33