import os
import tkinter as tk

import interface as inter
from . import customwidgets
from . import guifunctions as gf


def init(root, externals_path: str):
    # --------------------------------------------GENERAL TWEAKS--------------------------------------------
    root.columnconfigure(0, weight=1)
        
    # -----------------------------------------------APP MENU-----------------------------------------------
    # Main menu
    menu_main = tk.Menu(root)
    root.config(menu=menu_main)
        
    # File menu    
    menu_file = tk.Menu(menu_main, tearoff=False)
    
    menu_recent_files = tk.Menu(menu_file, tearoff=False)
    menu_recent_files.add_command(label="nothing")
    menu_recent_files.add_command(label="nothing")
    menu_recent_files.add_command(label="nothing")
    
    menu_file.add_command(label="New..."             , command=gf.menu_file_new)
    menu_file.add_command(label="Open..."            , command=gf.menu_file_open)
    menu_file.add_cascade(label="Recent files       ", menu=menu_recent_files)
    menu_file.add_command(label="Close"              , command=gf.menu_file_close)
    menu_file.add_command(label="Close all"          , command=gf.menu_file_close_all)
    menu_file.add_separator()
    menu_file.add_command(label="Save"               , command=gf.menu_file_save)
    menu_file.add_command(label="Save as..."         , command=gf.menu_file_save_as)
    menu_file.add_separator()
    menu_file.add_command(label="Exit"               , command=gf.menu_file_exit)
    
    
    # Add all menus
    menu_main.add_cascade(label="File", menu=menu_file)
    
    
    
    # --------------------------------------------ASEMBLER BUTTONS--------------------------------------------
    width_icon = 32
    height_icon = 32
    
    # Icon paths(needs to be global so doens't get garbage collected)
    global icon_assemble
    global icon_disassemble
    icon_assemble    = tk.PhotoImage(file=os.path.join(externals_path, "icons", "assemble.png"))
    icon_disassemble = tk.PhotoImage(file=os.path.join(externals_path, "icons", "disassemble.png"))
    
    # Main frame
    frame_assembler_buttons = tk.Frame(root)
    frame_assembler_buttons.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
    
    # Buttons
    button_assemble    = tk.Button(frame_assembler_buttons, image=icon_assemble   , width=width_icon, height=height_icon, command=gf.button_assemble)
    button_disassemble = tk.Button(frame_assembler_buttons, image=icon_disassemble, width=width_icon, height=height_icon, command=gf.button_disassemble)
    button_assemble   .pack(side="left")
    button_disassemble.pack(side="left", padx=5)
    
    
    
    # ---------------------------------PANNED WINDOW(TEXT EDITOR | TERMINAL)---------------------------------
    pwindow = tk.PanedWindow(root, orient="vertical", sashpad=10, sashwidth=8, sashrelief="sunken")
    pwindow.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="senw")
    root.rowconfigure(1, weight=1)
    
    # Text editor
    editor1 = customwidgets.TextEditor(pwindow)
    pwindow.add(editor1, minsize=200, stretch="always")
    
    # Terminal
    interface = inter.Interface()
    terminal = customwidgets.Terminal(pwindow, func=interface.command)
    pwindow.add(terminal, height=200, minsize=150, stretch="never")
    interface.set_output(terminal)
    interface.ping_thread_start()
    
    # -------------------------------------------------Status-------------------------------------------------
    label_status = tk.Label(root, text="Starting...", justify="right", anchor="e")
    label_status.grid(row=2, column=0, sticky="swe", padx=10)