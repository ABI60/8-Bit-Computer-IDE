"""
Module used to handle gui and other settings using "configparser".
- "init()" method should be used to initialize the filepath and the initial settings before using other methods.
- Default settings can be changed by changing the "settings_default" variable in the module.

---

    Available methods:
    - init()
    - reset()
    - retrieve()
    - save()
    - get()
    - replace()
"""
import os
import configparser


# Variables to be initialized by "init()"
settings_path = None
settings      = None


# Other variables
settings_file = "settings.cfg"
settings_default = {
    "Settings": 
        {
        "title"     : "Custom 8-Bit Computer IDE",
        "icon_file" : "icon.ico",
        "min_width" : "800",
        "min_height": "400",
        "width"     : "800",
        "height"    : "200",
        }
}


# -------------------------------------------------------------------------------------------
# -----------------------------------------FUNCTIONS-----------------------------------------
# -------------------------------------------------------------------------------------------
def init(externals_path:str, default:bool=False) -> None:
    """Initializes the settings for the project.

    Args:
        externals_path (str): Directory for the settings file.
        default (bool, optional): "True" -> Initialize settings as default | "False" -> Initialize settings from the file. Defaults to False.
    """
    global settings_path    
    global settings    
    settings_path = os.path.join(externals_path, settings_file)
    settings = configparser.ConfigParser()
    if default == True:
        reset()
    else:
        retrieve()
        
def reset() -> None:
    """Resets all settings to default."""
    global settings
    settings.read_dict(settings_default)

def retrieve() -> None:
    """Retrieves all settings from the initialized path."""
    # Dummy read since "configparser.read()" doesn't throw exceptions
    global settings
    with open(settings_path, 'r') as f:
        pass
    settings.read(settings_path)

def save() -> None:
    """Saves all settings to the initialized path."""
    global settings
    with open(settings_path, 'w') as f:
        settings.write(f)

def get(setting:str) -> str:
    """Returns the value of a setting."""
    global settings
    return settings["Settings"][setting]
        
def replace(setting:str, value:str) -> None:
    """Replaces the value of a setting."""
    global settings
    settings["Settings"][setting] = value
    