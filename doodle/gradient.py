
"""
A pillow utility for creating gradients.
"""

import math

from enum import Enum, auto
from PIL import Image
from PIL import ImageDraw

EPSILON = 1e-10

#todo: convert to hsl to interpolate

def interpolate(time, startValue, endValue, startTime, endTime, middle):
    t = (time - startTime) / (endTime - startTime);
    t = 0.5 * t / middle

    return startValue + t * (endValue - startValue);

def draw_gradient(width, height, type, points, rotation):
    if len(points) < 2:
        raise ValueError('all gradients must have at least two points')

    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    points.sort(key=lambda p: p.position)

    startIndex = 0
    endIndex = 1

    for i in range(width):
        start = points[startIndex]
        after = points[endIndex]

        if type == GradientType.LINEAR:
            startPosition = float(width) * start.position
            endPosition = float(width) * after.position

        percentage = (i - startPosition) / (endPosition - startPosition)
        pointIndex = int(len(points) * percentage)

        r = int(interpolate(percentage, start.colour[0], after.colour[0], 0, 1, start.middle))
        g = int(interpolate(percentage, start.colour[1], after.colour[1], 0, 1, start.middle))
        b = int(interpolate(percentage, start.colour[2], after.colour[2], 0, 1, start.middle))

        startA = start.colour[3] if len(start.colour) >= 4 else 255
        afterA = after.colour[3] if len(after.colour) >= 4 else 255
        a = int(interpolate(percentage, startA, afterA, 0, 1, start.middle))

        colour = (r, g, b, a)

        if type == GradientType.LINEAR:
            draw.line([(i, 0), (i, height)], fill=colour)

        if i >= endPosition:
            startIndex = min(startIndex + 1, len(points) - 1)
            endIndex = min(endIndex + 1, len(points) - 1)

    return image

class GradientType(Enum):
    """
    The different gradient types that can be drawn.
    """

    LINEAR = auto()
    ELLIPTICAL = auto()
    RADIAL = auto()
    CONICAL = auto()

class GradientPoint:
    """
    A point on a gradient.

    Attributes:
        position (float): The position on the gradient of this point,
            on a scale of 0 to 1.

        colour ((int, int, int)): The RGB tuple colour of this point.

        middle (float): The middle point of the colour interpolation
            between this point and the next in a gradient.
    """

    def __init__(self, position, colour, middle = 0.5):
        self.position = position
        self.colour = colour
        self.middle = middle
