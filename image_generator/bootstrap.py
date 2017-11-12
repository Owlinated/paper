import bpy
import os
import sys
# Bootstrap main script in blender

# Setup working directory
if bpy.context.space_data is not None:
    working_directory = os.path.dirname(bpy.context.space_data.text.filepath)
else:
    working_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(working_directory)
os.chdir(working_directory)

# Compile and execute script file
file = os.path.join(working_directory, 'main.py')
exec(compile(open(file).read(), 'main.py', 'exec'))
