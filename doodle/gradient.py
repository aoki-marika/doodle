
"""
A pillow utility for creating gradients.
"""

import math

from enum import Enum, auto
from PIL import Image
from PIL import ImageDraw

def interpolate(time, startValue, endValue, startTime, endTime):
    t = (time - startTime) / (endTime - startTime);
    return startValue + t * (endValue - startValue);

def draw_gradient(width, height, type, points):
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    points.sort(key=lambda p: p.position)

    beforeIndex = 0
    afterIndex = 1

    for i in range(width):
        before = points[beforeIndex]
        after = points[afterIndex]

        if type == GradientType.LINEAR:
            start = float(width) * before.position
            end = float(width) * after.position

        percentage = (i - start) / (end - start)
        pointIndex = int(len(points) * percentage)

        r = int(interpolate(percentage, before.colour[0], after.colour[0], 0, 1))
        g = int(interpolate(percentage, before.colour[1], after.colour[1], 0, 1))
        b = int(interpolate(percentage, before.colour[2], after.colour[2], 0, 1))
        colour = (r, g, b)

        if type == GradientType.LINEAR:
            draw.line([(i, 0), (i, height)], fill=colour)

        if i >= end:
            beforeIndex = min(beforeIndex + 1, len(points) - 1)
            afterIndex = min(afterIndex + 1, len(points) - 1)

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
        colour ((int, int, int)): The RGB tuple colour of this point.

        position (float): The position on the gradient of this point,
            on a scale of 0 to 1.

        midPoint (float): The midpoint of the colour interpolation between
            this point and the next in a gradient.
    """

    def __init__(self, colour, position, midPoint = 0.5):
        self.colour = colour
        self.position = position
        self.midPoint = midPoint
