
"""
A pillow utility for creating gradients.
"""

import math

from enum import Enum, auto
from PIL import Image
from PIL import ImageDraw

from .drawables import Axes

# todo: midpoints beyond 0.5 are broken

def gradient(percent, startValue, endValue, middle):
    """
    Get the gradient value between two colour channels.

    Args:
        percent (float): The point (from 0 to 1) between `startValue` and
            `endValue` to get the value of.

        startValue (float): The start value of the interpolation.

        endValue (float): The end value of the interpolation

        middle (float): The middle point of `startValue` between `startValue`
            and `endValue` (from 0 to 1).

    Returns:
        float: The value between `startValue` and `endValue` at `percent`,
            taking into account `middle`.
    """

    t = 0.5 * (percent / 1) / middle
    return startValue + t * (endValue - startValue);

def gradient_tuple(percent, start, end, middle):
    colour = ()

    for i in range(3):
        colour += (round(gradient(percent, start[i], end[i], middle)),)

    def alpha(colour):
        if len(colour) >= 4:
            return colour[3]
        else:
            return 255

    startA = alpha(start)
    endA = alpha(end)
    a = round(gradient(percent, startA, endA, middle))
    colour += (a,)

    return colour

def draw_gradient(width, height, type, points, direction = Axes.NONE):
    """
    Render a gradient to an `Image`.

    Args:
        width (int): The width of the gradient image.

        height (int): The height of the gradient image.

        type (GradientType): The type of this gradient.

        points ([GradientPoint]): An array of `GradientPoint`s used to draw the
            gradient.

        direction (Axes): The direction of the gradient. X for horizontal and Y
            for Vertical. Only used for `GradientType.LINEAR`.

    Returns:
        Image: A gradient made from the given arguments, rendered into an image.
    """

    if len(points) < 2:
        raise ValueError('all gradients must have at least two points')

    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    points.sort(key=lambda p: p.position)

    startIndex = 0
    endIndex = 1

    if type == GradientType.LINEAR:
        if direction == Axes.X:
            distance = width
        elif direction == Axes.Y:
            distance = height

    for i in range(distance):
        start = points[startIndex]
        end = points[endIndex]

        if type == GradientType.LINEAR:
            if direction == Axes.X:
                startPosition = float(width) * start.position
                endPosition = float(width) * end.position
            elif direction == Axes.Y:
                startPosition = float(height) * start.position
                endPosition = float(height) * end.position

        percentage = (i - startPosition) / (endPosition - startPosition)
        pointIndex = round(len(points) * percentage)

        colour = gradient_tuple(percentage, start.colour, end.colour, start.middle)

        if type == GradientType.LINEAR:
            if direction == Axes.X:
                start = (i, 0)
                end = (i, height)
            elif direction == Axes.Y:
                start = (0, i)
                end = (width, i)

            draw.line([start, end], fill=colour)

        if i >= endPosition:
            startIndex = min(startIndex + 1, len(points) - 1)
            endIndex = min(endIndex + 1, len(points) - 1)

    return image

class GradientType(Enum):
    """
    The different gradient types that can be drawn.
    """

    LINEAR = auto()

class GradientPoint:
    """
    A point on a gradient.

    Attributes:
        position (float): The position in the gradient of this point
            (from 0 to 1).

        colour ((int, int, int)): The RGB(A) tuple colour of this point.

        middle (float): The middle point of the colour interpolation
            between this point and the next in the gradient.
    """

    def __init__(self, position, colour, middle = 0.5):
        self.position = position
        self.colour = colour
        self.middle = middle
