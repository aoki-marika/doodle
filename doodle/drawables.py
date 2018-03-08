
from enum import Flag, auto
from PIL import Image

from .utils import round_tuple_values, paste_image

# todo: only recalculate draw/layout size/position when values change, not on every get

"""
Anything that can be drawn onto an <Image>.
"""
class Drawable:
	def __init__(self, width=0, height=0, x=0, y=0, **kwargs):
		self.parent = None
		self.size = (width, height)
		self.position = (x, y)
		self.anchor = Anchor.TOP_LEFT
		self.origin = Anchor.TOP_LEFT
		self.relativeSizeAxes = Axes.NONE
		self.margin = (0, 0, 0, 0)

		for key, value in kwargs.items():
			setattr(self, key, value)

	@property
	def width(self):
		"""
	    The X value of <size>.

	    :getter: Returns the X value of <size>.
	    :setter: Sets the X value of <size>.
	    :type: int or float
	    """

		return self.size[0]

	@width.setter
	def width(self, value):
		self.size = (value, self.size[1])

	@property
	def height(self):
		"""
	    The Y value of <size>.

	    :getter: Returns the Y value of <size>.
	    :setter: Sets the Y value of <size>.
	    :type: int or float
	    """

		return self.size[1]

	@height.setter
	def height(self, value):
		self.size = (self.size[0], value)

	@property
	def x(self):
		"""
	    The X value of <position>.

	    :getter: Returns the X value of <position>.
	    :setter: Sets the X value of <position>.
	    :type: int
	    """

		return self.position[0]

	@x.setter
	def x(self, value):
		self.position = (value, self.position[1])

	@property
	def y(self):
		"""
	    The Y value of <position>.

	    :getter: Returns the Y value of <position>.
	    :setter: Sets the Y value of <position>.
	    :type: int
	    """

		return self.position[1]

	@y.setter
	def y(self, value):
		self.position = (self.position[0], value)

	@property
	def draw_size(self):
		"""
		The size in pixels that this drawable will be drawn.
		
		:getter: Returns the draw size.
		:type: (int, int)
		"""

		size = self.size

		if self.relativeSizeAxes is not Axes.NONE:
			if self.parent is None:
				raise ValueError('cannot use relativeSizeAxes without having a parent')

			p = self.parent.children_size
			relativeWidth = p[0] * size[0]
			relativeHeight = p[1] * size[1]

			if self.relativeSizeAxes & Axes.X:
				size = (relativeWidth, size[1])

			if self.relativeSizeAxes & Axes.Y:
				size = (size[0], relativeHeight)

		return size

	@property
	def draw_position(self):
		"""
		The coordinates in pixels of <draw_size>, relative to <parent>.
		
		:getter: Returns the draw position.
		:type: (int, int)
		"""

		position = self.position

		if self.parent is not None:
			parentSize = self.parent.children_size
			parentPosition = self.parent.children_position
			size = self.draw_size
			anchor = self.anchor
			origin = self.origin

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

			originPosition = [a * b for a, b in zip(anchor_value(origin), size)]
			anchorPosition = [a * b for a, b in zip(anchor_value(anchor), parentSize)]
			anchorPosition = [a + b for a, b in zip(anchorPosition, parentPosition)]
			anchorOriginPosition = [a - b for a, b in zip(anchorPosition, originPosition)]
			position = [a + b for a, b in zip(anchorOriginPosition, position)]

		# place the draw position correctly inside margin
		marginX = 0
		marginY = 0

		if self.anchor & Anchor.X_LEFT:
			marginX = self.margin[2]
		elif self.anchor & Anchor.X_RIGHT:
			marginX = -self.margin[3]

		if self.anchor & Anchor.Y_TOP:
			marginY = self.margin[0]
		elif self.anchor & Anchor.Y_BOTTOM:
			marginY = -self.margin[1]

		position = (position[0] + marginX, position[1] + marginY)

		return position

	@property
	def layout_size(self):
		"""
		The size in pixels of this drawable.
		
		:getter: Returns the layout size.
		:type: (int, int)
		"""

		s = self.draw_size

		return (s[0] + (self.margin[2] + self.margin[3]), s[1] + (self.margin[0] + self.margin[1]))

	@property
	def layout_position(self):
		"""
		The coordinates in pixels of <layout_size>, relative to <parent>.
		
		:getter: Returns the layout position.
		:type: (int, int)
		"""

		p = self.draw_position

		return (p[0] - self.margin[2], p[1] - self.margin[0])

	"""
	Render this drawable into an <Image>.

	:returns: This drawable rendered into an <Image>.
	"""
	def render(self):
		raise NotImplementedError('Drawable subclasses must implement render')

"""
A type of <Drawable> that can have children <Drawable>s.
"""
class Container(Drawable):
	def __init__(self, children=[], **kwargs):
		self.padding = (0, 0, 0, 0)
		self.masking = True

		super(Container, self).__init__(**kwargs)
		self.children = []

		for child in children:
			self.add(child)

	@property
	def children_size(self):
		"""
		The size in pixels that the children of this container are allowed to occupy.
		
		:getter: Returns the children size.
		:type: (int, int)
		"""

		s = self.draw_size

		return (s[0] - (self.padding[2] + self.padding[3]), s[1] - (self.padding[0] + self.padding[1]))

	@property
	def children_position(self):
		"""
		The coordinates in pixel of <children_size>, relative to <parent>.
		
		:getter: Returns the children size.
		:type: (int, int)
		"""

		p = self.draw_position

		return (self.padding[2], self.padding[0])

	@property
	def render_size(self):
		"""
		The size in pixels of this container when being rendered.

		This is specially added for <masking> so we can easily climb the
		parent tree, and shouldn't be used for anything else.
		
		:getter: Returns the render size.
		:type: (int, int)
		"""

		if not self.masking and self.parent:
			return self.parent.render_size
		else:
			return self.draw_size

	@property
	def render_position(self):
		"""
		The coordinates in pixels of <render_size>, relative to <parent>.
		
		:getter: Returns the render position.
		:type: (int, int)
		"""

		if not self.masking:
			if self.parent:
				return [a + b for a, b in zip(self.parent.render_position, self.draw_position)]
			else:
				return self.draw_position
		else:
			return self.draw_position

	"""
	Add a child view.

	:param child: The <Drawable> to add.
	"""
	def add(self, child):
		child.parent = self
		self.children.append(child)

	"""
	Remove a child view.

	:param child: The <Drawable> to remove.
	:raises ValueError: If <child> is not in this containers children.
	"""
	def remove(self, child):
		if child.parent is not self:
			raise ValueError('cannot remove a child that is not in this Container')

		child.parent = None
		self.children.remove(child)

	def render(self):
		container = Image.new('RGBA', round_tuple_values(self.render_size), (255, 255, 255, 0))

		for child in self.children:
			if self.masking and (self.parent and self.parent.masking):
				position = child.draw_position
			else:
				if isinstance(child, Container) and not child.masking:
					position = (0, 0)
				else:
					position = [a + b for a, b in zip(self.render_position, child.draw_position)]

			container = paste_image(container, child.render(), round_tuple_values(position))

		return container

"""
A type of <Drawable> that draws as a box with a colour.
"""
class Box(Drawable):
	def __init__(self, colour, **kwargs):
		super(Box, self).__init__(**kwargs)
		self.colour = colour

	def render(self):
		return Image.new('RGB', round_tuple_values(self.draw_size), self.colour)

"""
A relative point in a box.
"""
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

"""
Two dimensional axes.
"""
class Axes(Flag):
	NONE = 0
	X = auto()
	Y = auto()
	BOTH = X | Y
