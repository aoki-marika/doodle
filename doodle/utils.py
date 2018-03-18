
"""
Basic general utilities for doodle.
"""

from PIL import Image

def round_tuple_values(inputTuple):
    """
    Round all the values in a tuple.

    Args:
        inputTuple ((float, float)): The tuple to round the values of.

    Returns:
        (int, int): `inputTuple` with all its values rounded.
    """

    return tuple(round(v) for v in inputTuple)

def paste_image(background, foreground, position):
    """
    Paste an `Image` onto another `Image` with alpha compositing.

    Args:
        background (Image): The image to paste onto.

        foreground (Image): The image to paste.

        position ((int, int)): The coordinates relative to `background` to paste
            `foreground` at.

    Returns:
        Image: The alpha composited image.
    """

    temp = Image.new('RGBA', background.size, (255, 255, 255, 0))
    temp.paste(foreground, position)
    return Image.alpha_composite(background, temp)
