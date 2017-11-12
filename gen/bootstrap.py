import bpy
import os
import sys
# Bootstrap main script in blender

# Setup working directory
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(cwd)
os.chdir(cwd)

# Compile and execute script file
file = os.path.join(cwd, 'main.py')
exec(compile(open(file).read(), 'main.py', 'exec'))
