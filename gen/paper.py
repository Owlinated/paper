import bpy
import sys
import random
from math import pi
TAU = 2*pi

def randomPaper(width = 2.97, height = 2.10, deviation = .1):
    return paramSurface(height, width, \
        random.gauss(0, deviation), random.gauss(0, deviation), random.gauss(0, deviation), \
        random.gauss(0, deviation), random.gauss(0, deviation), random.gauss(0, deviation))

def generate(n, m, surfaceGen):
    minHeight = getSurfaceHeight(n, m, surfaceGen)
    mesh = createSurface(n, m, minHeight, surfaceGen)
    return minHeight, mesh

# Create a function for the u, v surface parameterization from r0 and r1
def paramSurface(width, height, x1, x2, x3, y1, y2, y3):
    def surface(u, v):
        u = 2 * u - 1
        v = 2 * v - 1
        point = (u * height, \
                 v * width, \
                 u * x1 + u ** 2 * x2 + u ** 3 * x3 + v * y1 + v ** 2 * y2 + v ** 3 * y3)
        return point
    return surface

# Find min height of surface
def getSurfaceHeight(n, m, surface):
    height = sys.maxsize
    for col in range(m):
        for row in range(n):
            u = row / n
            v = col / m
            point = surface(u, v)
            if point[2] < height: height = point[2]
    return height

# Create an object from a surface parameterization
def createSurface(n, m, height, surface):
    verts = list()
    faces = list()

    # Create uniform n by m grid
    for col in range(m):
        for row in range(n):
            u = row / n
            v = col / m

            # Create vertex with function
            point = surface(u, v)
            point = (point[0], point[1], point[2] - height)
            verts.append(point)

            # Create face
            rowNext = row + 1
            colNext = col + 1

            if rowNext < n and colNext < m:
                faces.append(((col*n) + rowNext, \
                            (colNext*n) + rowNext, \
                            (colNext*n) + row, \
                            (col*n) + row))

    print('verts : ' + str(len(verts)))
    print('faces : ' + str(len(faces)))

    # Create mesh and object
    mesh = bpy.data.meshes.new('PaperMesh')
    obj  = bpy.data.objects.new('Paper', mesh)
    # Link object to scene
    bpy.context.scene.objects.link(obj)
    # Create mesh from given verts and faces
    mesh.from_pydata(verts, [], faces)
    #Update mesh with new data
    mesh.update(calc_edges=True)
    return obj
