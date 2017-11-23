import bpy
import os
import sys
# This is the entry point for blenders script execution
# Either run this from within blender or use it with blenders cli

# Setup working directory
if bpy.context.space_data is not None:
    working_directory = os.path.dirname(bpy.context.space_data.text.filepath)
    script = 'demo.py'
else:
    working_directory = os.path.dirname(os.path.abspath(__file__))
    script = 'main.py'
sys.path.append(working_directory)
os.chdir(working_directory)

# Compile and execute script file
file = os.path.join(working_directory, script)
exec(compile(open(file).read(), script, 'exec'))
