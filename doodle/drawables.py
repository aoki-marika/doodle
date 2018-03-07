
from enum import Enum
from PIL import Image

def round_tuple_values(inputTuple):
	return tuple(round(v) for v in inputTuple)

def paste_image(background, foreground, position):
	temp = Image.new('RGBA', background.size, (255, 255, 255, 0))
	temp.paste(foreground, position)
	return Image.alpha_composite(background, temp)

class Drawable:
	def __init__(self, **kwargs):
		self.parent = None
		self.size = (0, 0)
		self.position = (0, 0)
		self.anchor = Anchor.TOP_LEFT
		self.origin = Anchor.TOP_LEFT
		self.relativeSizeAxis = Axis.NONE

		for key, value in kwargs.items():
			setattr(self, key, value)

	@property
	def calculatedSize(self):
		size = self.size

		if self.relativeSizeAxis is not Axis.NONE:
			if self.parent is None:
				raise ValueError('cannot use relativeSizeAxis without having a parent')

			p = self.parent.calculatedSize
			relativeWidth = p[0] * size[0]
			relativeHeight = p[1] * size[1]

			if self.relativeSizeAxis is Axis.X:
				size[0] = relativeWidth
			elif self.relativeSizeAxis is Axis.Y:
				size[1] = relativeHeight
			elif self.relativeSizeAxis is Axis.BOTH:
				size = (relativeWidth, relativeHeight)

		return size

	def render(self):
		raise NotImplementedError('Drawable subclasses must implement render')

class Container(Drawable):
	def __init__(self, children=[], **kwargs):
		super(Container, self).__init__(**kwargs)
		self.children = []

		for child in children:
			self.add(child)

	def add(self, child):
		child.parent = self
		self.children.append(child)

	def remove(self, child):
		if child.parent is not self:
			raise ValueError('cannot remove a child that is not in this Container')

		child.parent = None
		self.children.remove(child)

	def render(self):
		container = Image.new('RGBA', round_tuple_values(self.calculatedSize), (255, 255, 255, 0))

		for child in self.children:
			container = paste_image(container, child.render(), child.position)

		return container

class Box(Drawable):
	def __init__(self, colour, **kwargs):
		super(Box, self).__init__(**kwargs)
		self.colour = colour

	def render(self):
		return Image.new('RGB', round_tuple_values(self.calculatedSize), self.colour)

class Anchor(Enum):
	TOP_LEFT = 0
	TOP_CENTER = 1
	TOP_RIGHT = 2
	CENTER_LEFT = 3
	CENTER = 4
	CENTER_RIGHT = 5
	BOTTOM_LEFT = 6
	BOTTOM = 7
	BOTTOM_RIGHT = 8

class Axis(Enum):
	NONE = 0
	X = 1
	Y = 2
	BOTH = 3
