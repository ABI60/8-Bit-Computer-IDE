# - Help command when used on its own will look for the variable name "application" to print.
# - "help all" command will look for the string "Description: " and pull between 1-60 characters 
#   after it. Make sure to include this string, or it will show "***Info missing!***" instead!


application               = ("- Application: Custom Assembler Project\n"+
                                  "- Subscribe to \"youtube.com/Microesque\"\n"+
                                  "- Type \"help all\" to see the available commands!")

command_quit              = ("- Stands for: Quit\n"+
                                  "- Description: Closes the application.")

command_list_ports        = ("- Stands for: List ports\n"+
                                  "- Description: Lists all available ports.")

command_help              = "No information is available yet!"
command_connect           = "No information is available yet!"
command_disconnect        = "No information is available yet!"
command_settings          = "No information is available yet!"
command_connection_status = "No information is available yet!"
command_programmer_ping   = "No information is available yet!"
command_programmer_reset  = "No information is available yet!"