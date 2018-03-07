
from enum import Enum

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

class Container(Drawable):
	def __init__(self, children=[], **kwargs):
		super(Container, self).__init__(**kwargs)
		self.children = []

		for child in children:
			self.add(child)

	def add(self, child):
		child.parent = self
		self.children.append(child)

class Box(Drawable):
	def __init__(self, colour, **kwargs):
		super(Box, self).__init__(**kwargs)
		self.colour = colour

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
