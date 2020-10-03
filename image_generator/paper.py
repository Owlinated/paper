import random
import sys

import bpy
from bpy.types import Mesh


def create_random_paper(width=2.97, height=2.10, deviation=.1):
    """Create a random paper generator

    Args:
        width: Width of mesh
        height: Height of mesh
        deviation: Standard deviation of parameters 

    Returns:
        Surface generation function
    """
    return create_paper(height, width,
                        random.gauss(0, deviation), random.gauss(
                            0, deviation), random.gauss(0, deviation),
                        random.gauss(0, deviation), random.gauss(0, deviation), random.gauss(0, deviation))


# Create a function for the u, v surface parametrization from r0 and r1
def create_paper(width, height, x1, x2, x3, y1, y2, y3):
    """Create a parameterized paper generator

    Args:
        width: Width of mesh
        height: Height of mesh

    Returns:
        Surface generation function
    """

    def surface(u, v):
        u = 2 * u - 1
        v = 2 * v - 1
        point = (u * height,
                 v * width,
                 u * x1 + u ** 2 * x2 + u ** 3 * x3 + v * y1 + v ** 2 * y2 + v ** 3 * y3)
        return point

    return surface


def generate(n, m, surface_gen):
    """Generate a sheet of paper from generator function

    Args:
        n: Number of horizontal samples
        m: Number of vertical samples
        surface_gen: Paper generation function

    Returns:
        A tuple of the minimum height and the generated mesh
    """
    min_height = get_surface_height(n, m, surface_gen)
    mesh = create_surface(n, m, min_height, surface_gen)
    return min_height, mesh


def get_surface_height(n, m, surface_gen):
    """Find minimum height of surface

    Args:
        n: Number of horizontal samples
        m: Number of vertical samples
        surface_gen: Paper generation function

    Returns:
        Minimum height in mesh
    """
    height = sys.maxsize
    for col in range(m):
        for row in range(n):
            u = row / n
            v = col / m
            point = surface_gen(u, v)
            if point[2] < height:
                height = point[2]
    return height


# Create an object from a surface parametrization
def create_surface(n, m, height, surface_gen):
    """Create mesh from generator function and add it to scene

    Args:
        n: Number of horizontal samples
        m: Number of vertical samples
        height: Minimum height in mesh used as offset
        surface_gen: Paper generation function

    Returns:
        Generated mesh
    """
    vertices = list()
    faces = list()

    # Create uniform n by m grid
    for col in range(m):
        for row in range(n):
            u = row / n
            v = col / m

            # Create vertex with function
            point = surface_gen(u, v)
            point = (point[0], point[1], point[2] - height)
            vertices.append(point)

            # Create face
            rowNext = row + 1
            colNext = col + 1

            if rowNext < n and colNext < m:
                faces.append(((col * n) + rowNext,
                              (colNext * n) + rowNext,
                              (colNext * n) + row,
                              (col * n) + row))

    print('vertices : ' + str(len(vertices)))
    print('faces : ' + str(len(faces)))

    # Create mesh and object
    mesh: Mesh = bpy.data.meshes.new('PaperMesh')
    obj = bpy.data.objects.new('Paper', mesh)

    # Link object to scene
    bpy.context.scene.collection.objects.link(obj)

    # Create mesh from given vertices and faces
    mesh.from_pydata(vertices, [], faces)

    # Update mesh with new data
    mesh.update(calc_edges=True)

    # Render mesh smooth
    for polygon in mesh.polygons:
        polygon.use_smooth = True

    return obj
