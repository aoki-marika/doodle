
import os

import xml.etree.ElementTree as ET

from doodle import Drawable, Container, Box, Texture, Text, Anchor, Axes
from PIL import Image

"""
Get an <Anchor> from a string.

:param string: The string to parse.
:returns: An <Anchor> if <string> matched one, or <None> if not.
"""
def anchor_from_string(string):
	if string:
		anchors = {
			'top-left': Anchor.TOP_LEFT,
			'top-center': Anchor.TOP_CENTER,
			'top-right': Anchor.TOP_RIGHT,
			'center-left': Anchor.CENTER_LEFT,
			'center': Anchor.CENTER,
			'center-right': Anchor.CENTER_RIGHT,
			'bottom-left': Anchor.BOTTOM_LEFT,
			'bottom-center': Anchor.BOTTOM_CENTER,
			'bottom-right': Anchor.BOTTOM_RIGHT,
		}

		string = string.lower()
		if string in anchors:
			return anchors[string]
		else:
			return None
	else:
		return None

"""
Get an <Axes> from a string.

:param string: The string to parse.
:returns: An <Axes> if <string> matched one, or <None> if not.
"""
def axes_from_string(string):
	if string:
		axes = {
			'none': Axes.NONE,
			'x': Axes.X,
			'y': Axes.Y,
			'both': Axes.BOTH,
		}

		string = string.lower()
		if string in axes:
			return axes[string]
		else:
			return None
	else:
		return None

"""
Get an RGB tuple from an RGB hex.

:param string: The RGB hex to parse.
:returns: An RGB tuple parsed from <string>.
"""
def colour_from_string(string):
	string = string.lstrip('#')
	return tuple(int(string[i : i + 2], 16) for i in (0, 2, 4))

"""
Get a <Boolean> from a string.

:param string: The string to parse.
:returns: Whether <string> is 'true' or not.
"""
def bool_from_string(string):
	return string.lower() == 'true'

"""
Get an <Element> from an XML node.

:param xml: The XML to get an <Element> for.
:returns: An <Element> from <xml>.
"""
def element_from_xml(xml):
	elements = {
		'container': ContainerElement,
		'box': BoxElement,
		'texture': TextureElement,
	}

	return elements[xml.tag](xml)

"""
A <Drawable> that is loaded from an XML node.
"""
class Element(Drawable):
	"""
	:param xml: The XML node to parse to get the properties of this element.
	"""
	def __init__(self, xml):
		super(Element, self).__init__()
		self.anchor = anchor_from_string(xml.get('anchor')) or Anchor.TOP_LEFT
		self.origin = anchor_from_string(xml.get('origin')) or Anchor.TOP_LEFT
		self.x = float(xml.get('x') or 0)
		self.y = float(xml.get('y') or 0)
		self.width = float(xml.get('width') or 0)
		self.height = float(xml.get('height') or 0)
		self.relativeSizeAxes = axes_from_string(xml.get('relative-size-axes')) or Axes.NONE

		if 'margin' in xml.attrib:
			m = float(xml.get('margin'))
			self.margin = (m, m, m, m)
		else:
			self.margin = (
				float(xml.get('margin-top') or 0),
				float(xml.get('margin-bottom') or 0),
				float(xml.get('margin-left') or 0),
				float(xml.get('margin-right') or 0),
			)

	"""
	Load this elements attributes that are dependant on a <Drawing>.

	:param drawing: The <Drawing> to load with.
	"""
	def load(self, drawing):
		return

"""
A <Container> variant of <Element>.
"""
class ContainerElement(Element, Container):
	def __init__(self, xml):
		super(Container, self).__init__()
		super(ContainerElement, self).__init__(xml)

		if 'padding' in xml.attrib:
			p = float(xml.get('padding'))
			self.padding = (p, p, p, p)
		else:
			self.padding = (
				float(xml.get('padding-top') or 0),
				float(xml.get('padding-bottom') or 0),
				float(xml.get('padding-left') or 0),
				float(xml.get('padding-right') or 0),
			)

		for node in xml:
			self.add(element_from_xml(node))

	def load(self, drawing):
		for child in self.children:
			child.load(drawing)

"""
A <Box> variant of <Element>.
"""
class BoxElement(Element, Box):
	def __init__(self, xml):
		super(Box, self).__init__()
		super(BoxElement, self).__init__(xml)

		self.colour = colour_from_string(xml.get('colour') or '')

"""
A <Texture> variant of <Element>.
"""
class TextureElement(Element, Texture):
	def __init__(self, xml):
		super(Texture, self).__init__()
		super(TextureElement, self).__init__(xml)

		self.file = xml.get('file')
		self.sizeToImage = bool_from_string(xml.get('size-to-image') or '')

	def load(self, drawing):
		self.image = Image.open(os.path.join(drawing.path, self.file))

"""
A special <ContainerElement> that loads a file.
"""
class Drawing(ContainerElement):
	"""
	:param file: The path to the file to load.
	"""
	def __init__(self, file):
		if os.path.exists(file):
			tree = ET.parse(file)
			root = tree.getroot()

			if root.tag == 'drawing':
				if 'width' in root.attrib and 'height' in root.attrib:
					super(Drawing, self).__init__(root)
					self.path = os.path.dirname(file)
					self.load(self)
				else:
					raise ValueError('drawing files must specify a width and height in the root <drawing> node')
			else:
				raise ValueError('drawing files must have a root <drawing> node')
		else:
			raise ValueError('file does not exist')
