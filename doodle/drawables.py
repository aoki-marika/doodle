
from enum import Flag, auto
from PIL import Image

def _round_tuple_values(inputTuple):
	return tuple(round(v) for v in inputTuple)

def _paste_image(background, foreground, position):
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
	def calculated_size(self):
		size = self.size

		if self.relativeSizeAxis is not Axis.NONE:
			if self.parent is None:
				raise ValueError('cannot use relativeSizeAxis without having a parent')

			p = self.parent.calculated_size
			relativeWidth = p[0] * size[0]
			relativeHeight = p[1] * size[1]

			if self.relativeSizeAxis & Axis.X:
				size = (relativeWidth, size[1])

			if self.relativeSizeAxis & Axis.Y:
				size = (size[0], relativeHeight)

		return size

	@property
	def calculated_position(self):
		position = self.position

		if self.parent is not None:
			p = self.parent.calculated_size
			s = self.calculated_size
			a = self.anchor
			o = self.origin

			def anchor_value(anchor):
				if anchor & Anchor.X_LEFT:
					anchorX = 0
				elif anchor & Anchor.X_CENTER:
					anchorX = 0.5
				elif anchor & Anchor.X_RIGHT:
					anchorX = 1

				if anchor & Anchor.Y_TOP:
					anchorY = 0
				elif anchor & Anchor.Y_CENTER:
					anchorY = 0.5
				elif anchor & Anchor.Y_BOTTOM:
					anchorY = 1

				return (anchorX, anchorY)

			anchorPosition = [a * b for a, b in zip(anchor_value(a), s)]
			originPosition = [a * b for a, b in zip(anchor_value(o), p)]
			position = [a - b for a, b in zip(originPosition, anchorPosition)]

		return position

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
		container = Image.new('RGBA', _round_tuple_values(self.calculated_size), (255, 255, 255, 0))

		for child in self.children:
			container = _paste_image(container, child.render(), _round_tuple_values(child.calculated_position))

		return container

class Box(Drawable):
	def __init__(self, colour, **kwargs):
		super(Box, self).__init__(**kwargs)
		self.colour = colour

	def render(self):
		return Image.new('RGB', _round_tuple_values(self.calculated_size), self.colour)

class Anchor(Flag):
	X_LEFT = auto()
	X_CENTER = auto()
	X_RIGHT = auto()

	Y_TOP = auto()
	Y_CENTER = auto()
	Y_BOTTOM = auto()

	TOP_LEFT = X_LEFT | Y_TOP
	TOP_CENTER = X_CENTER | Y_TOP
	TOP_RIGHT = X_RIGHT | Y_TOP

	CENTER_LEFT = X_LEFT | Y_CENTER
	CENTER = X_CENTER | Y_CENTER
	CENTER_RIGHT = X_RIGHT | Y_CENTER

	BOTTOM_LEFT = X_LEFT | Y_BOTTOM
	BOTTOM_CENTER = X_CENTER | Y_BOTTOM
	BOTTOM_RIGHT = X_RIGHT | Y_BOTTOM

class Axis(Flag):
	NONE = 0
	X = auto()
	Y = auto()
	BOTH = X | Y
