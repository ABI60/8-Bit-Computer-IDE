import re


# Check the page: https://docs.python.org/3/library/re.html
# and find "Writing a Tokenizer" for more info about the implementation

# Check the page: https://stackabuse.com/python-string-interpolation-with-the-percent-operator/
# For how to use % with strings for the "join" method below

# Token types for the tokenizer
# - If more types are needed, add them ass a class variable and to the specification below
#   > Types have to be strings, as the regex group names only accept strings
#   > Specification list is checked sequentially(the last value is essentially the default and should be '.')
#     so, if a new type's pattern will conflict with another, put the priority one above
class TOKEN_TYPE:
    # Token types
    ID        = "ID"
    LITERAL   = "LITERAL"
    SEPERATOR = "SEPERATOR"
    SKIP      = "SKIP"
    INVALID   = "INVALID"
    
    # "type"-"pattern" list for each type
    SPECIFICATIONS = (
        (ID       , r"[a-zA-Z_]+"),
        (LITERAL  , r"\d+"    ),
        (SEPERATOR, r','      ),
        (SKIP     , r'\s'     ),
        (INVALID  , r'.'      ),
    )
    
# Join all the patterns by OR'ing them as groups(while naming each group)
pattern = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_TYPE.SPECIFICATIONS)

def tokenize(line: str, row: int):
    """Returns the list of tokens for the given assembly line.(Tokens also consist of tuples)
    - Removes comments from the line
    - To use or see the possible types, type "from mytokenizer import TOKEN_TYPE" and look at its variables

    Args:
        line (str): Assembly line to tokenize.
        row (int): Row index of the assembly line.(Needed for exception information)

    Returns:
        List[Tuple[str, str, int, int, str]]: Tuple parameters -> (type, value, row, column, line)
    """
    # Remove all comments
    comment_start = line.find(";")
    if comment_start != -1:
        line = line[:comment_start]
    
    # Find all patters in the line
    tokens = []
    for match in re.finditer(pattern, line):
        type = match.lastgroup
        value = match.group()
        column = match.start()+1
        if type == TOKEN_TYPE.SKIP:
            continue
        else:
            tokens.append((type, value, row, column, line.replace("\n", "")))        
    return tokens