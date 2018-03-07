
from enum import Flag, auto
from PIL import Image

# todo: autosize axes
# todo: debug drawing (visualise anchors and origins, among other things)
# todo: disable/enable masking

def _round_tuple_values(inputTuple):
	return tuple(round(v) for v in inputTuple)

def _paste_image(background, foreground, position):
	temp = Image.new('RGBA', background.size, (255, 255, 255, 0))
	temp.paste(foreground, position)
	return Image.alpha_composite(background, temp)

class Drawable:
	def __init__(self, width=0, height=0, x=0, y=0, **kwargs):
		self.parent = None
		self.size = (width, height)
		self.position = (x, y)
		self.anchor = Anchor.TOP_LEFT
		self.origin = Anchor.TOP_LEFT
		self.relativeSizeAxes = Axes.NONE

		for key, value in kwargs.items():
			setattr(self, key, value)

	@property
	def draw_size(self):
		size = self.size

		if self.relativeSizeAxes is not Axes.NONE:
			if self.parent is None:
				raise ValueError('cannot use relativeSizeAxes without having a parent')

			p = self.parent.draw_size
			relativeWidth = p[0] * size[0]
			relativeHeight = p[1] * size[1]

			if self.relativeSizeAxes & Axes.X:
				size = (relativeWidth, size[1])

			if self.relativeSizeAxes & Axes.Y:
				size = (size[0], relativeHeight)

		return size

	@property
	def draw_position(self):
		position = self.position

		if self.parent is not None:
			p = self.parent.draw_size
			s = self.draw_size
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
			anchorOriginPosition = [a - b for a, b in zip(originPosition, anchorPosition)]
			position = [a + b for a, b in zip(anchorOriginPosition, position)]

		return position

	def render(self):
		raise NotImplementedError('Drawable subclasses must implement render')

class Container(Drawable):
	def __init__(self, children=[], **kwargs):
		self.autoSizeAxes = Axes.NONE

		super(Container, self).__init__(**kwargs)
		self.children = []

		for child in children:
			self.add(child)

	@property
	def draw_size(self):
		size = super(Container, self).draw_size

		if self.autoSizeAxes is not Axes.NONE:
			# if auto size and relative size are on the same axis
			if self.relativeSizeAxes & Axes.X and self.autoSizeAxes & Axes.X or self.relativeSizeAxes & Axes.Y and self.autoSizeAxes & Axes.Y:
				raise ValueError('cannot use relativeSizeAxes and autoSizeAxes on the same Axes')

			# todo: autosize calculation

		return size

	def add(self, child):
		child.parent = self
		self.children.append(child)

	def remove(self, child):
		if child.parent is not self:
			raise ValueError('cannot remove a child that is not in this Container')

		child.parent = None
		self.children.remove(child)

	def render(self):
		container = Image.new('RGBA', _round_tuple_values(self.draw_size), (255, 255, 255, 0))

		for child in self.children:
			container = _paste_image(container, child.render(), _round_tuple_values(child.draw_position))

		return container

class Box(Drawable):
	def __init__(self, colour, **kwargs):
		super(Box, self).__init__(**kwargs)
		self.colour = colour

	def render(self):
		return Image.new('RGB', _round_tuple_values(self.draw_size), self.colour)

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

class Axes(Flag):
	NONE = 0
	X = auto()
	Y = auto()
	BOTH = X | Y
