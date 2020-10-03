import mathutils
import paper
import util


def setup_scene():
    # Create camera
    target = util.ensure_target()
    util.ensure_camera((0, 0, 10), target)

    # Create light
    util.ensure_light(origin=(0, 0, 10))

    # Create backdrop
    util.ensure_cube()

    # Create paper
    paperGen = paper.create_random_paper()
    minHeight = util.ensure_paper(paperGen)

    def adjust_height(world): return mathutils.Vector(
        (world[0], world[1], world[2] - minHeight))

    # Return lambda that maps paper coordinates to world
    return lambda coord: adjust_height(paperGen(*coord))

    # TODO
    # Setup scene (backdrop, sheet, camera)
    # Repeat x times
    # Randomize scene (Mostly normal distribution)
    # Random background texture (solid, textures)
    # Random backdrop material (glossy, matte)
    # Random lights
    # Count
    # Type
    # Position
    # Color
    # Direction
    # Random sheet textures
    # Random surface
    # Random camera position
    # Lookat position
    # Distance from sheet
    # Position on half spehere
    # Rotation around lookat axis
    # Random camera parameters (start with fixed to iphone 6s plus)
    # Render image
    # Keep track of surface parameters and edge positions
    # Create tfrecord file
