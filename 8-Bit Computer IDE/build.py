import os
import PyInstaller.__main__
import shutil
import subprocess


# Construct the current directory(application), the destination directory(build) and others...
application_name = "Custom 8-Bit Computer IDE"
application_path = os.path.dirname(os.path.realpath(__file__))
destination_path = os.path.join(application_path, "executable")
executable_path  = os.path.join(destination_path, "dist", application_name, f"{application_name}.exe")
externals_folder = os.path.join(application_path, "externals")


# Remove the destination folder if exists
try:
    shutil.rmtree(destination_path)
except FileNotFoundError:
    ...


# Construct relevant paths
script_path     = os.path.join(application_path, "main.py")
icon_path       = os.path.join(externals_folder, "icon.ico")
dist_path       = os.path.join(destination_path, "dist")
work_path       = os.path.join(destination_path, "temp")
spec_path       = os.path.join(destination_path, "spec")


# Run pyinstaller
PyInstaller.__main__.run([
    "--onedir",
    "--windowed",
    f"--name={application_name}",
    f"{script_path}",
    f"--icon={icon_path}",
    f"--distpath={dist_path}",
    f"--workpath={work_path}",
    f"--specpath={spec_path}",
    f"--add-data={externals_folder};.",
])


# Run the executable
subprocess.check_call(executable_path)