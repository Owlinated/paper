import bpy
import os
import sys

# Specify the script to be executed
scriptFile = "main.py"

# Check if script is executed in Blender and get absolute path of current folder
if bpy.context.space_data is not None:
    cwd = os.path.dirname(bpy.context.space_data.text.filepath)
else:
    cwd = os.path.dirname(os.path.abspath(__file__))

sys.path.append(cwd)
# Change current working directory to scripts folder
os.chdir(cwd)

# Compile and execute script file
file = os.path.join(cwd, scriptFile)
exec(compile(open(file).read(), scriptFile, 'exec'))
