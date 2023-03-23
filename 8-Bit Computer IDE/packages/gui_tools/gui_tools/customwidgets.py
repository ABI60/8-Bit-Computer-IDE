import tkinter as tk
from tkinter import ttk
import threading


class TextEditor(tk.Frame):
    def __init__(self, *args, **kwargs):
        """Subclass of "tk.Frame". Creates a text editor window with x and y scrolls."""
        super().__init__(*args, **kwargs)
    
        # Initialize editor elements
        self.config(bd=5, relief="sunken")
        self.rowconfigure   (0, weight=1)
        self.columnconfigure(0, weight=1)
        
        editor_textbox = tk.Text(self)    
        editor_xscroll = ttk.Scrollbar(self, command=editor_textbox.xview, orient="horizontal")
        editor_yscroll = ttk.Scrollbar(self, command=editor_textbox.yview)

        editor_textbox.config(xscrollcommand=editor_xscroll.set, yscrollcommand=editor_yscroll.set, undo=True, wrap="none", font=("Courier", 12))

        editor_textbox.grid(row=0, column=0, sticky="nwes")
        editor_xscroll.grid(row=1, column=0, sticky="ews")
        editor_yscroll.grid(row=0, column=1, sticky="ens")
        
        
class Terminal(tk.Frame):
    # References
    # Example: Logging Window: https://tkdocs.com/tutorial/text.html
    # tag_config() : https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/text-methods.html
    def __init__(self, *args, func, **kwargs):  
        """Subclass of "tk.Frame". Creates a text editor window with x and y scrolls and a command entry.
        - Requires the extra argument "func", which is the function to be called when the user gives an input
        - Log screen will be disabled and can't be written to, use the entry below for user inputs
        
            Available methods:
            - write()
            - cls()
        
            Available tags:
            - "normal"    
            - "input_mark"
            - "input"     
            - "error"     
            - "exception" 
        """      
        super().__init__(*args, **kwargs)
    
        # Initialize terminal elements
        self.rowconfigure   (0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.text_log           = tk.Text(self, bg="#DFDFDF", selectbackground="#8B8B8B")
        self.scroll_log_yscroll = tk.Scrollbar(self, width=14)
        self.scroll_log_xscroll = tk.Scrollbar(self, width=14)
        self.text_input         = tk.Text(self, bg="#FAFAFA", selectbackground="#8B8B8B", height=1, pady=3, bd=2, relief="sunken")

        self                   .config(bd=5, relief="sunken")
        self.text_log          .config(xscrollcommand=self.scroll_log_xscroll.set, yscrollcommand=self.scroll_log_yscroll.set, undo=True, wrap="none")
        self.scroll_log_xscroll.config(command=self.text_log.xview, orient="horizontal")
        self.scroll_log_yscroll.config(command=self.text_log.yview)
        self.text_input        .config(undo=True, wrap="none", font=("Courier", 12))

        self.text_log          .grid(row=0, column=0, sticky="nwes")
        self.scroll_log_xscroll.grid(row=1, column=0, sticky="ews")
        self.scroll_log_yscroll.grid(row=0, column=1, sticky="ens")
        self.text_input        .grid(row=2, column=0, sticky="wes", pady=(5,0))
        
        # Configure tags
        self.text_log.tag_configure("normal"    , font=("Courier New"     , 11, "bold"))
        self.text_log.tag_configure("input_mark", font=("Courier New"     , 12, "bold"), foreground="#0000C6", lmargin1=3, offset=-1)
        self.text_log.tag_configure("input"     , font=("Courier New"     , 12, "bold"))
        self.text_log.tag_configure("error"     , font=("Courier New"     , 11, "bold"), foreground="#BF0000")
        self.text_log.tag_configure("exception" , font=("Cooper Std Black", 11, "bold"), foreground="#BF0000", lmargin1=15)
        
        # Set binds
        self.text_input.bind("<Return>" , self._on_input_enter)
        self.text_input.bind("<<Paste>>", self._on_input_paste)
        self.text_input.bind("<Up>"     , self._on_input_up_arrow)
        self.text_input.bind("<Down>"   , self._on_input_down_arrow)
        
        # Other configurations
        self._lock_write = threading.Lock()
        self.func = func
        self.maxlog = 51        #real value is this-1
        self.maxbuffer = 11     #real value is this-1
        self.input_buffer = []
        self.input_buffer_cursor = 0
        self.text_log["state"] = "disabled"
        
    def write(self, msg, tag="normal"):
        """Writes the massage onto the terminal with the given tag's font.
        - Tag defaults to normal
        - Terminal will be scrolled to the end automatically
        - Thread safe
        """
        def _write():
            self.text_log["state"] = "normal"
            
            # Log the message and scroll down
            self.text_log.insert("end", msg, tag)
            if tag == "exception":
                self.text_log.insert("end", "\n\n", tag)
            self.text_log.see("end")
            
            # Delete old entries to keep within maxlog
            numlines = int(self.text_log.index("end - 1 line").split('.')[0])        
            if numlines > self.maxlog:
                self.text_log.delete(1.0, 1.0+(numlines-self.maxlog))
            
            self.text_log["state"] = "disabled"
        with self._lock_write:
            self.after(0, _write)
    
    def cls(self):
        """Clears the logs."""
        self.text_log["state"] = "normal"
        self.text_log.delete("1.0", "end")        
        self.text_log["state"] = "disabled"
        
    def _on_input_enter(self, _):
        """Handler for "enter(return)" event on terminal input."""
        # Log user input with appropriate tags
        input = self.text_input.get("1.0", "end-1c")
        self.text_input.delete("1.0", "end")
        self.write("> ", tag="input_mark")
        self.write(input + '\n', tag="input")
        
        # Input handling
        if input == "cls":
            self.cls()
        elif input == "q":
            import sys
            sys.exit(0)
        else:
            def _thread_func():
                try:
                    self.func(input)
                except Exception as err:
                    self.write(str(err), "exception")
            threading.Thread(target=_thread_func).start()
        
        # Add the input to the buffer if not empty, set cursor to None(indicates not initialized)
        self.input_buffer_cursor = None
        try:
            last_entry = self.input_buffer[-1]
        except IndexError:
            last_entry = ""
        if input != "" and input != last_entry:
            self.input_buffer.append(input)
            if len(self.input_buffer) == self.maxbuffer:
                self.input_buffer.pop(0)
        
        # Stop other events
        return "break"
    
    def _on_input_paste(self, _):
        """Handler for "paste(ctrl+v)" event on terminal input."""
        # Delete the selected text if any
        try:
            sel_first = self.text_input.index("sel.first")
            sel_last  = self.text_input.index("sel.last")
            self.text_input.delete(sel_first, sel_last)
        except tk.TclError:
            pass
        
        # Insert the clipboard on cursor if its valid(remove anything after a newline if exists)
        try:
            clipboard = self.clipboard_get()
            newline_index = clipboard.find('\n')
            insert_index = self.text_input.index("insert")
            if newline_index != -1:
                self.text_input.insert(insert_index, clipboard[:newline_index])
            else:
                self.text_input.insert(insert_index, clipboard)
        except tk.TclError:
            pass
        
        # Stop other events
        return "break"
    
    def _on_input_up_arrow(self, _):
        """Handler for "up arrow" event on terminal input."""
        # Skip if no previous inputs
        if len(self.input_buffer) == 0:
            return "break"
        
        # If cursor not initialized, set it to last entry, otherwise decrement the cursor
        if self.input_buffer_cursor == None:
            self.input_buffer_cursor = len(self.input_buffer) - 1
        else:
            self.input_buffer_cursor -= 1
            if self.input_buffer_cursor < 0:
                self.input_buffer_cursor = 0
        
        # Update the terminal input with buffered command
        input = self.input_buffer[self.input_buffer_cursor]
        self.text_input.delete("1.0", "end")
        self.text_input.insert("end", input)
        
        # Stop other events
        return "break"
               
    def _on_input_down_arrow(self, _):
        """Handler for "down arrow" event on terminal input."""
        # Skip if no previous inputs
        if len(self.input_buffer) == 0:
            return "break"
        
        # Skip if cursor not initialized, otherwise increment the cursor
        if self.input_buffer_cursor == None:
            return "break"
        else:
            self.input_buffer_cursor += 1
            if self.input_buffer_cursor > len(self.input_buffer) - 1:
                self.input_buffer_cursor = len(self.input_buffer) - 1

        # Update the terminal input with buffered command
        input = self.input_buffer[self.input_buffer_cursor]
        self.text_input.delete("1.0", "end")
        self.text_input.insert("end", input)
        
        # Stop other events
        return "break"