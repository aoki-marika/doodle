
import os
import textwrap

import xml.etree.ElementTree as ET

from enum import Enum, Flag, auto
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from .utils import round_tuple_values, paste_image

# todo: only recalculate draw/layout size/position when values change, not on every get

class Drawable:
	"""
	Anything that can be drawn onto an <Image>.
	"""

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

	def render(self):
		"""
		Render this drawable into an <Image>.

		:returns: This drawable rendered into an <Image>.
		"""

		raise NotImplementedError('Drawable subclasses must implement render')

class Container(Drawable):
	"""
	A type of <Drawable> that can have children <Drawable>s.
	"""

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

	def add(self, child, index=-1):
		"""
		Add a child view.

		:param child: The <Drawable> to add.
		:param index: The index in <children> to insert <child> at.
		"""

		child.parent = self

		if index == -1:
			self.children.append(child)
		else:
			self.children.insert(index, child)

	def remove(self, child):
		"""
		Remove a child view.

		:param child: The <Drawable> to remove.
		:raises ValueError: If <child> is not in this containers children.
		"""

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

class Box(Drawable):
	"""
	A type of <Drawable> that draws as a box with a colour.
	"""

	def __init__(self, colour=(255, 255, 255), **kwargs):
		super(Box, self).__init__(**kwargs)
		self.colour = colour

	def render(self):
		return Image.new('RGB', round_tuple_values(self.draw_size), self.colour)

class Texture(Drawable):
	"""
	A type of <Drawable> that draws an <Image>.
	"""

	def __init__(self, sizeToImage=False, **kwargs):
		self._image = None
		self.sizeToImage = sizeToImage

		super(Texture, self).__init__(**kwargs)

	@property
	def image(self):
		"""
		The <Image> that this texture should draw.

		:getter: Returns this textures image.
		:setter: Sets this textures image.
		:type: Image
		"""

		return self._image

	@image.setter
	def image(self, value):
		self._image = value

		if self.sizeToImage:
			self.size = value.size

	def render(self):
		return self.image.resize(round_tuple_values(self.draw_size), Image.ANTIALIAS)

class TextMode(Enum):
	"""
	Display modes for <Text>.
	"""

	SINGLE_LINE = auto()
	SQUISH = auto()
	WRAP = auto()

class Text(Drawable):
	"""
	A type of <Drawable> that can draw text with fonts.

	When using <TextMode.SINGLE_LINE>, you should not change the width or height.
	When using <TextMode.SQUISH>, you should not change the height.
	"""

	def __init__(self, fontPath='', textColour=(255, 255, 255), textSize=0, text='', mode=TextMode.SINGLE_LINE, lineSpacing=0, **kwargs):
		"""
		:param fontPath: The path to the true-type font to use to draw this text.
		:param textColour: The colour to draw the text with.
		:param textSize: The height in pixels to draw the text with.
		:param text: The text to draw.
		:param mode: The <TextMode> to draw the text with.
		:param lineSpacing: the vertical line spacing when using <TextMode.WRAP>, unused otherwise.
		"""

		super(Text, self).__init__(**kwargs)

		# init the parameters so we dont crash when calling <apply_size> without all the parameters set
		self.font = None
		self._fontPath = None
		self.textColour = None
		self._textSize = None
		self._text = None

		self.mode = mode
		self.lineSpacing = lineSpacing
		self.fontPath = fontPath
		self.textColour = textColour
		self.textSize = textSize
		self.text = text

	@property
	def fontPath(self):
		"""
		The path of the font that this text should use when drawing text.

		:getter: Returns this texts font path.
		:setter: Sets this texts font path.
		:type: string
		"""

		return self._fontPath

	@fontPath.setter
	def fontPath(self, value):
		self._fontPath = value
		self.update_font()
		self.apply_size()

	@property
	def textSize(self):
		"""
		The height in pixels that this text should be drawn with.

		:getter: Returns this texts size.
		:setter: Sets this texts size.
		:type: int
		"""

		return self._textSize

	@textSize.setter
	def textSize(self, value):
		self._textSize = value
		self.update_font()
		self.apply_size()

	@property
	def text(self):
		"""
		The text for this text to display.

		:getter: Returns this texts text.
		:setter: Sets this texts text.
		:type: string
		"""

		return self._text

	@text.setter
	def text(self, value):
		self._text = value
		self.apply_size()

	def update_font(self):
		"""
		Update the <ImageFont> used for drawing text, and store it in <font>.
		"""

		if self.fontPath and self.textSize:
			if os.path.exists(self.fontPath):
				self.font = ImageFont.truetype(self.fontPath, self.textSize)
		else:
			return None

	def apply_size(self):
		"""
		Correctly set the size of this text to fit <text> using <font>.
		"""

		if self.text:
			# wrap does not use text size, so dont bother calculating it
			if self.font and self.mode is not TextMode.WRAP:
				s = self.font.getsize(self.text)

				if self.mode == TextMode.SINGLE_LINE:
					self.size = s
				elif self.mode == TextMode.SQUISH:
					self.size = (self.size[0], s[1])

	def render(self):
		def text_image(text):
			"""
			Get an <Image> for given text drawn in this <Text>s specified styling.

			:param text: The text to get an image of.
			"""

			temp = Image.new('RGBA', self.font.getsize(text), (255, 255, 255, 0))
			draw = ImageDraw.Draw(temp)
			draw.text((0, 0), text, self.textColour, font=self.font)

			return temp

		def anchored_position(imageSize, parentSize):
			"""
			Get the anchored position of an image on either the X or Y axis.

			:param imageSize: The width or height of the image to get the position of.
			:param parentSize: The width or height of the parent to anchor <imageSize> inside of.
			:returns: The anchored position of <imageSize>, relative to <parentSize>.
			"""

			if self.anchor & Anchor.X_LEFT or self.anchor & Anchor.Y_TOP:
				return 0
			elif self.anchor & Anchor.X_CENTER or self.anchor & Anchor.Y_CENTER:
				return int((parentSize - imageSize) / 2)
			elif self.anchor & Anchor.X_RIGHT or self.anchor & Anchor.Y_BOTTOM:
				return parentSize - imageSize

		def horizontal_position(image):
			"""
			Get the horizontal anchored position of an <Image> using <anchor>.

			:param image: The <Image> to get the anchored position of.
			:returns: The horizontal anchored position of <image>.
			"""

			return anchored_position(image.size[0], size[0])

		def vertical_position(image):
			"""
			<horizontal_position>, but the vertical anchored position.
			"""

			return anchored_position(image.size[1], size[1])

		size = round_tuple_values(self.draw_size)
		drawImage = Image.new('RGBA', size, (255, 255, 255, 0))

		if self.mode == TextMode.WRAP:
			# get an estimate of how many characters there should be per-line
			limit = int(size[0] / self.font.getsize('a')[0])

			textHeight = 0
			lineImages = []

			# get all the line images and the height of textImage
			for line in textwrap.wrap(self.text, width=limit):
				lineImage = text_image(line)
				textHeight += lineImage.size[1] + self.lineSpacing
				lineImages.append(lineImage)

			textHeight = max(textHeight - self.lineSpacing, 0)
			textImage = Image.new('RGBA', (size[0], textHeight), (255, 255, 255, 0))

			lineY = 0

			for lineImage in lineImages:
				textImage = paste_image(textImage, lineImage, (horizontal_position(lineImage), lineY))
				lineY += lineImage.size[1] + self.lineSpacing
		else:
			textImage = text_image(self.text)

			# squish the text if we are squishing and the text needs to be squished
			if self.mode == TextMode.SQUISH and size[0] < textImage.size[0]:
				textImage = textImage.resize((size[0], textImage.size[1]), Image.ANTIALIAS)

		# correctly horizontally and vertically place the text image
		return paste_image(drawImage, textImage, (horizontal_position(textImage), vertical_position(textImage)));

class SpriteText(Drawable):
	"""
	A type of <Drawable> that can draw text with image files.
	"""

	def __init__(self, fontPath='', text='', **kwargs):
		super(SpriteText, self).__init__(**kwargs)

		# same as <Text>, set the values beforehand so we can reference them in <update_size> without everything set
		self.font = None
		self._fontPath = None
		self._text = None

		self.fontPath = fontPath
		self.text = text

	@property
	def fontPath(self):
		"""
		The path to the sprite font that this sprite text should use.

		:getter: Returns this sprite texts font path.
		:setter: Sets this sprite texts font path.
		:type: string
		"""

		return self._fontPath

	@fontPath.setter
	def fontPath(self, value):
		self._fontPath = value

		if self.fontPath:
			self.font = SpriteFont(self.fontPath)
			self.update_size()
		else:
			self.font = None
			self.size = (0, 0)

	@property
	def text(self):
		"""
		The text for this sprite text to display.

		:getter: Returns this sprite texts text.
		:setter: Sets this sprite texts text.
		:type: string
		"""

		return self._text

	@text.setter
	def text(self, value):
		self._text = value
		self.update_size()

	def update_size(self):
		if self.text and self.font:
			self.size = self.font.get_size(self.text)

	def render(self):
		return self.font.get_image(self.text)

class SpriteFont:
	"""
	A font for <SpriteText>.
	"""

	def __init__(self, path):
		"""
		:param path: The path to the sprite fonts folder.
		"""

		file = os.path.join(path, 'font.xml')
		if os.path.exists(file):
			tree = ET.parse(file)
			root = tree.getroot()

			if root.tag == 'font':
				if 'width' in root.attrib and 'height' in root.attrib and 'spacing' in root.attrib:
					self.characterSize = (int(root.get('width')), int(root.get('height')))
					self.characterSpacing = int(root.get('spacing'))
					self.characterFiles = dict((n.get('value'), n.text) for n in root.iter('character'))
					self.path = path
				else:
					raise ValueError('the root <font> node in font.xml must specify \'width\', \'height\', and \'spacing\' attributes')
			else:
				raise ValueError('font.xml must contain a root <font> node')
		else:
			raise ValueError(f'could not find a font.xml in \'{path}\'')

	def get_size(self, text):
		"""
		Get the size of a given string if it were drawn with this sprite font.

		:param text: The text to get the size of.
		:returns: The size of <text> in this sprite font.
		"""

		return ((self.characterSize[0] + self.characterSpacing) * len(str(text)) + abs(self.characterSpacing), self.characterSize[1])

	def get_image(self, text):
		"""
		Get an <Image> for text drawn with this sprite font.

		:param text: The text to draw.
		:returns: An <Image> with <text> drawn with this sprite font.
		"""

		image = Image.new('RGBA', self.get_size(text), (255, 255, 255, 0))

		lastX = 0
		for char in text:
			file = f'{char}.png'

			if char in self.characterFiles:
				file = self.characterFiles[char]

			file = os.path.join(self.path, file)

			if os.path.exists(file):
				image = paste_image(image, Image.open(file), (lastX, 0))
				lastX += (self.characterSize[0] + self.characterSpacing)
			else:
				raise ValueError(f'could not find file \'{file}\' for character \'{char}\'')

		return image

class Anchor(Flag):
	"""
	A relative point in a box.
	"""

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
	"""
	Two dimensional axes.
	"""

	NONE = 0
	X = auto()
	Y = auto()
	BOTH = X | Y
