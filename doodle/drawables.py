
"""
A library for creating view hierarchies and rendering them into static images.
"""

import os
import textwrap

import xml.etree.ElementTree as ET

from enum import Enum, Flag, auto
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from .gradient import draw_gradient
from .utils import round_tuple_values, paste_image

# todo: only recalculate draw/layout/render size/position when values change, not on every get

class Drawable:
    """
    Anything that can be rendered into a static image.

    Args:
        Drawable arguments are done in a way that allows quickly creating large
        draw hierarchies, and is reminiscent of C# object initializers. The
        `kwargs` are all used to set the attribute of their key to their value,
        which allows quickly doing things such as below:

        Container(
            width=400,
            height=400,
            children=[
                Box(
                    relativeSizeAxes=Axes.BOTH,
                    size=(1, 1),
                    colour=(255, 255, 255),
                ),
            ],
        )

        which creates a 400x400 container with a white fill. Although it may not
        seem like much in a small example like this, it is very useful for
        large and or complex hierarchies.

    Attributes:
        anchor (Anchor): The point in `parent` that `origin` should center on.
            Defaults to `Anchor.TOP_LEFT`.

        margin ((int, int, int, int)): The top, bottom, left, and right margins
            of this drawable, respectively.
            Defaults to (0, 0, 0, 0).

        origin (Anchor): The point in this drawable that the position should be
            anchored to.
            Defaults to `Anchor.TOP_LEFT`.

        parent (Container): The parent of this drawable.
            Defaults to None.

        position ((int, int)): The position of this drawable, relative to
            `parent` and `anchor`/`origin`.
            Defaults to (0, 0).

        relativeSizeAxes: Control which `Axes` are relatively sized using
            `parent`s size (from 0 to 1).
            Defaults to `Axes.NONE`.

        size ((float, float)): The size of this drawable.
            Defaults to (0, 0).
    """

    def __init__(self, width=0, height=0, x=0, y=0, **kwargs):
        self.parent = None
        self.size = (width, height)
        self.position = (x, y)
        self.anchor = Anchor.TOP_LEFT
        self.origin = Anchor.TOP_LEFT
        self.relativeSizeAxes = Axes.NONE
        self.margin = (0, 0, 0, 0)
        self.gradientType = None
        self.gradientPoints = None
        self.gradientDirection = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def width(self):
        """float: The X (first) value of `size`."""
        return self.size[0]

    @width.setter
    def width(self, value):
        self.size = (value, self.size[1])

    @property
    def height(self):
        """float: The Y (second) value of `size`."""
        return self.size[1]

    @height.setter
    def height(self, value):
        self.size = (self.size[0], value)

    @property
    def x(self):
        """int: The X (first) value of `position`."""

        return self.position[0]

    @x.setter
    def x(self, value):
        self.position = (value, self.position[1])

    @property
    def y(self):
        """int: The Y (second) value of `position`."""
        return self.position[1]

    @y.setter
    def y(self, value):
        self.position = (self.position[0], value)

    @property
    def draw_size(self):
        """(int, int): The size in pixels that this drawable will be drawn with
            when rendering."""

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
        """(int, int): The coordinates in pixels of `draw_size`, relative to
            `parent`."""

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
        """(int, int): The size in pixels of this drawable to use when
            calculating layout."""

        s = self.draw_size

        return (s[0] + (self.margin[2] + self.margin[3]), s[1] + (self.margin[0] + self.margin[1]))

    @property
    def layout_position(self):
        """(int, int): The coordinates in pixels of `layout_size`, relative to
            `parent`."""

        p = self.draw_position

        return (p[0] - self.margin[2], p[1] - self.margin[0])

    def get_gradient(self, width, height):
        if self.gradientType and self.gradientPoints:
            return draw_gradient(width, height, self.gradientType, self.gradientPoints, self.gradientDirection)

        return None

    def render(self):
        """
        Render this drawable into an `Image`.

        This method must be implemented by subclasses.

        Returns:
            Image: The render result.
        """

        raise NotImplementedError('Drawable subclasses must implement render')

class Container(Drawable):
    """
    A type of `Drawable` that can have children `Drawable`s.

    Attributes:
        children ([Drawable]): All the children of this container. Should not
            be set directly from outside the class, but instead manipulated by
            `Container.add` and `Container.remove`.
            Defaults to an empty list.

        padding ((int, int, int, int)): The top, bottom, left, and right padding
            of this container, respectively.
            Defaults to `(0, 0, 0, 0)`

        masking (bool): Whether or not this container should mask its children.
            For a container to mask means for it to clip off its children that
            extend outside of its bounds. Disabling masking of course disables
            this functionality for this container and its children can draw
            outside of its bounds. This option only affects this container, not
            the parent or children containers.
            Defaults to `True`.
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
        """(int, int): The size in pixels that the children of this container
            are allowed to occupy."""

        s = self.draw_size

        return (s[0] - (self.padding[2] + self.padding[3]), s[1] - (self.padding[0] + self.padding[1]))

    @property
    def children_position(self):
        """(int, int): The coordinates in pixels of `children_size`, relative to
            `parent`."""

        return (self.padding[2], self.padding[0])

    @property
    def render_size(self):
        """
        (int, int): The size in pixels of this container when being rendered.

        This is specially added for `masking` so we can recursively climb the
        parent tree and use their sizes, and shouldn't be used for anything
        else.
        """

        if not self.masking and self.parent:
            return self.parent.render_size
        else:
            return self.draw_size

    @property
    def render_position(self):
        """
        (int, int): The coordinates in pixels of <render_size>, relative to
            <parent>.

        Like `render_size`, this is specially added for traversing parents
        recursively and using their position, and should not be used for
        anything else.
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
        Add a child drawable.

        Args:
            child (Drawable): The drawable to add as a child.

            index (int): The index in `children` to insert `child` at, -1 is the
                end of the array.
                Defaults to -1.
        """

        child.parent = self

        if index == -1:
            self.children.append(child)
        else:
            self.children.insert(index, child)

    def remove(self, child):
        """
        Remove a child drawable.

        Args:
            child (Drawable): The child drawable to remove.

        Raises:
            ValueError: If `child` is not one of this containers children.
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
    A type of `Drawable` that draws as a box with a colour.

    Supports gradients.

    Attributes:
        colour ((int, int, int)): The RGB tuple colour to draw with.
            Defaults to `(255, 255, 255)`.
    """

    def __init__(self, colour=(255, 255, 255), **kwargs):
        super(Box, self).__init__(**kwargs)
        self.colour = colour

    def render(self):
        size = round_tuple_values(self.draw_size)
        gradient = self.get_gradient(size[0], size[1])

        if gradient:
            return gradient
        else:
            return Image.new('RGB', size, self.colour)

class Texture(Drawable):
    """
    A type of `Drawable` that draws an `Image`.

    Attributes:
        sizeToImage (bool): Whether or not this texture should automatically
            resize to the size of its image.
    """

    def __init__(self, sizeToImage=False, **kwargs):
        self._image = None
        self.sizeToImage = sizeToImage

        super(Texture, self).__init__(**kwargs)

    @property
    def image(self):
        """Image: The `Image` that this texture should draw."""
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
    Display modes for `Text`.

    Attributes:
        SINGLE_LINE: Draw the text on a single line and auto-size the `Text` to
            fit it.

        SQUISH: Draw the text on a single line and auto-size the `Text`s height
            to fit, but squish it horizontally if its too big to display in the
            `Text`s `width`.

        WRAP: Wrap the text to fit the `Text`s width.
    """

    SINGLE_LINE = auto()
    SQUISH = auto()
    WRAP = auto()

class Text(Drawable):
    """
    A type of `Drawable` that can draw text with true type fonts.

    Notes:
        When using `TextMode.SINGLE_LINE`, you should not change the width or
            height.

        When using `TextMode.SQUISH`, you should not change the height.

    Attributes:
        textColour ((int, int, int)): The RGB tuple colour to draw the text
            with.
            Defaults to (255, 255, 255).

        lineSpacing (int): The vertical space in pixels between lines when using
            `TextMode.WRAP`, unused otherwise.
            Defaults to 0.
    """

    def __init__(self, fontPath='', textColour=(255, 255, 255), textSize=0, text='', mode=TextMode.SINGLE_LINE, lineSpacing=0, **kwargs):
        super(Text, self).__init__(**kwargs)

        # init the parameters so we dont crash when calling <update_size> without all the parameters set
        self.font = None
        self._fontPath = None
        self.textColour = None
        self._textSize = None
        self._text = None
        self._mode = None

        self.lineSpacing = lineSpacing
        self.fontPath = fontPath
        self.textColour = textColour
        self.textSize = textSize
        self.text = text
        self.mode = mode

    @property
    def fontPath(self):
        """str: The path of the TTF file of the font that this text should use
            when drawing text."""

        return self._fontPath

    @fontPath.setter
    def fontPath(self, value):
        self._fontPath = value
        self.update_font()
        self.update_size()

    @property
    def textSize(self):
        """int: The height in pixels that this text should draw its font with."""
        return self._textSize

    @textSize.setter
    def textSize(self, value):
        self._textSize = value
        self.update_font()
        self.update_size()

    @property
    def text(self):
        """str: The text for this text to display."""
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.update_size()

    @property
    def mode(self):
        """TextMode: The mode for this text to use."""
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        self.update_size()

    def update_font(self):
        """
        Get the `ImageFont` specified by `fontPath` and `textSize`, and store it
        in `font`.
        """

        if self.fontPath and self.textSize:
            if os.path.exists(self.fontPath):
                self.font = ImageFont.truetype(self.fontPath, self.textSize)

    def update_size(self):
        """
        Update this size of this text to fit `text` using `font`.
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
            Get an `Image` for given text drawn in this texts specified styling.

            Args:
                text (str): The text to get an image of.

            Returns:
                Image: An image of `text`.
            """

            temp = Image.new('RGBA', self.font.getsize(text), (255, 255, 255, 0))
            draw = ImageDraw.Draw(temp)
            draw.text((0, 0), text, self.textColour, font=self.font)

            return temp

        def anchored_position(imageSize, parentSize):
            """
            Get the anchored position of an image on either the X or Y axis
            using `anchor`.

            Args:
                imageSize (float): The width or height of the image to get the
                    position of.

                parentSize (float): The width or height of the parent to anchor
                    `imageSize` inside of.

            Returns:
                float: The anchored position of `imageSize`, relative to
                    `parentSize`.
            """

            if self.anchor & Anchor.X_LEFT or self.anchor & Anchor.Y_TOP:
                return 0
            elif self.anchor & Anchor.X_CENTER or self.anchor & Anchor.Y_CENTER:
                return int((parentSize - imageSize) / 2)
            elif self.anchor & Anchor.X_RIGHT or self.anchor & Anchor.Y_BOTTOM:
                return parentSize - imageSize

        def horizontal_position(image):
            return anchored_position(image.size[0], size[0])

        def vertical_position(image):
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

            # draw all the line images
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
    A type of `Drawable` that can draw text with a `SpriteFont`.

    Notes:
        You should not change the size of this drawable as it automatically
        resizes to fit its text.
    """

    def __init__(self, font=None, text='', **kwargs):
        super(SpriteText, self).__init__(**kwargs)

        # same as `Text`, set the values beforehand so we can reference them in `update_size` without everything set
        self._font = None
        self._text = None

        self.font = font
        self.text = text

    @property
    def font(self):
        """SpriteFont: The sprite font this sprite text should draw with."""
        return self._font

    @font.setter
    def font(self, value):
        self._font = value
        self.update_size()

    @property
    def text(self):
        """str: The text for this sprite text to display."""
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.update_size()

    def update_size(self):
        """
        Update the size of this sprite text to fit `text` using `font`.
        """

        if self.text and self.font:
            self.size = self.font.get_size(self.text)

    def render(self):
        return self.font.get_image(self.text)

class SpriteFont:
    """
    A font for `SpriteText`.

    Creating a Sprite Font:
        Sprite fonts are a special kind of file used by drawables for simple
        usage of fonts that are composed of static images.

        To create a sprite font, you first need to make a font.xml file. This
        file specifies the different properties of the font such as character
        size and spacing. The contents of the file should look something like
        this:

        <font width="..." height="..." spacing="...">
            ...
        </font>

        replacing width, height and spacing with the values for your specific
        font.

        Now with that setup, you can add your glyph files. These files should
        all be the same resolution as specified by the width and height
        attributes in the font file, placed in the same directory as the
        font file, and named as the character they represent (e.g. 'a' would
        be 'a.png', 'b' would be 'b.png', etc.) Though there are some characters
        that won't work with this, such as system reserved characters in
        filenames like '/'. This is where the font file comes in again. You can
        map specific characters to specific files using character nodes in the
        font node, as seen below:

        <character value="...">file.png</character>

        replacing the value attribute with the character you want to map (e.g.
        value="/"), and the contents of the node with the name of the file you
        want to map it to (e.g. 'slash.png'). The result of this example should
        look something like this:

        <font width="..." height="..." spacing="...">
            <character value="/">slash.png</character>
        </font>

        Note that character nodes are entirely optional, and only needed for
        fonts that want to display system reserved filename characters.

        Now after adding all your glyphs your font is ready to be used in
        drawables. Simply create a `SpriteFont` with the directory to the
        folder containing the font file, and you should be good to go.

    Attributes:
        path (str): The path to this sprite fonts folder.

        characterSize ((int, int)): The size in pixels of every character in
            this font.

        characterSpacing (int): The horizontal spacing in pixels between every
            character in this font.

        characterFiles ({str: str}): All the specified character files from the
            font file, if any.
    """

    def __init__(self, path):
        """
        Raises:
            ValueError: If the font at `path` is invalid in any way.
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

        Args:
            text (str): The text to get the size of.

        Returns
            (int, int): The size in pixels of `text`.
        """

        return ((self.characterSize[0] + self.characterSpacing) * len(str(text)) + abs(self.characterSpacing), self.characterSize[1])

    def get_image(self, text):
        """
        Get an `Image` for text drawn with this sprite font.

        Args:
            text (str): The text to draw.

        Returns:
            Image: An image of `text` drawn with this sprite font.
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
