import math

TILT_ANGLE = math.radians(15)

def marker_pos(c, plane_marker):
    c = (c[0]/2047, c[1]/127, c[2]/2047)
    c = rescale_coordinates(c)
    if plane_marker:
        c = (c[0], 0, c[2])
    c = rotate_axes(c)
    x_,y_,z_ = c

    # I have no idea why this scaling is necessary but it is
    x_ = x_*math.cos(TILT_ANGLE)
    y_ = y_*math.cos(TILT_ANGLE)
    
    c = to_screen_coords(x_, y_)
    return c[0], c[1]

def yellow_dot_pos(c):
    """Returns coordinates for the centre of the yellow dot on the
minimap when at portal coordinate c = (xxx, yy, zzz).

Returned coordinate (x,y) uses the standard for a bitmap image, with
both coordinates in the range [0, 1] and (0,0) as the top left and
(1,1) as the bottom right.

Coordinate should be scaled to the square working region in the
centre of the minimap image.
"""
    return marker_pos(c, False)

def white_dot_pos(c):
    """Returns coordinates for the centre of the white dot and
ellipse on the minimap when at portal coordinate c = (xxx, yy, zzz).

Returned coordinate (x,y) uses the standard for a bitmap image, with
both coordinates in the range [0, 1] and (0,0) as the top left and
(1,1) as the bottom right.

Coordinate should be scaled to the square working region in the
centre of the minimap image.
"""
    return marker_pos(c, True)

def rescale_coordinate(to_scale, i, j):
    """Rescale a coordinate based on the other two.

to_scale: The coordinate to re-scale.
i, j: The other two coordinates.
"""
    return to_scale*math.sqrt(abs(i**2 * j**2 / 3 + 1 - (i**2)/2 -(j**2)/2))

def rescale_coordinates(c):
    """Applies the coordinate rescaling to all axes."""
    x,y,z = c
    x_ = rescale_coordinate(x, y, z)
    y_ = rescale_coordinate(y, x, z)
    z_ = rescale_coordinate(z, x, y)
    return (x_, y_, z_)

def rotate_axes(c, tilt=TILT_ANGLE):
    # Rotate around x axis, based on Rx from
    # https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions
    x,y,z = c

    x_ = x
    y_ = y*math.cos(tilt) - z*math.sin(tilt)
    z_ = y*math.sin(tilt) + z*math.cos(tilt)
    return (x_, y_, z_)

def to_screen_coords(x, y):
    """Convert a camera coordinate, with (-1,-1) and (1,1) as
the bottom left and top right corners, to screen coordinates,
with (0,0) and (1,1) as the top left and bottom right corners.
"""
    return (1+x)/2, (1-y)/2
