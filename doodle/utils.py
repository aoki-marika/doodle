
from PIL import Image

"""
Round all the values in a tuple.

:param inputTuple: The tuple to round the values of.
:returns: <inputTuple> with all its values rounded.
"""
def round_tuple_values(inputTuple):
	return tuple(round(v) for v in inputTuple)

"""
Paste an <Image> onto another <Image> with alpha compositing.

:param background: The <Image> to paste on to.
:param foreground: The <Image> to paste.
:param position: The coordinates relative to <background> to paste <foreground> at.
:returns: The alpha composited <Image>.
"""
def paste_image(background, foreground, position):
	temp = Image.new('RGBA', background.size, (255, 255, 255, 0))
	temp.paste(foreground, position)
	return Image.alpha_composite(background, temp)
