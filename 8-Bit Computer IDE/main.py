import os, sys
import tkinter as tk

from gui_tools import settings
from gui_tools import guielements


# Assign paths depending on the app info
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    application_path = sys._MEIPASS
    externals_path   = application_path
else:
    application_path = os.path.dirname(os.path.realpath(__file__))
    externals_path   = os.path.join(application_path, "externals")
    
    
# Tkinter initializations
settings.init(externals_path, default=False)
root = tk.Tk()
root.title(settings.get("title"))
root.iconbitmap(os.path.join(externals_path, settings.get("icon_file")))
root.geometry("{0}x{1}".format(settings.get("width"), settings.get("height")))
root.minsize(settings.get("min_width"), settings.get("min_height"))

guielements.init(root, externals_path)

root.mainloop()