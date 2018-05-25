
"""
A framework built on top of drawables for creating view hierarchies from specially formatted files.

For every element its name is the same as the `Drawable` it subclasses from, but
the name is in lisp-case. For attributes its the same, they represent a property
of their `Drawable` base class in lisp-case. Any exceptions to this rule are
listed in the docstring of their respective `Element` subclass.

For attributes that are of a special type, see the respective `*_from_string`
method for details on formatting.
"""

import operator
import os

import xml.etree.ElementTree as ET

from doodle import Drawable, Container, Box, Texture, Text, SpriteText, SpriteFont, Anchor, Axes, TextMode
from .gradient import Direction, GradientType, GradientStop
from PIL import Image

def anchor_from_string(string):
    """
    Get an `Anchor` from a string.

    Args:
        string (str): The string to parse.

    Returns:
        Anchor: An anchor if `string` matched one, or None if not.
    """

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

def axes_from_string(string):
    """
    Get an `Axes` from a string.

    Args:
        string (str): The string to parse.

    Returns:
        Axes: An axes if `string` matched one, or None if not.
    """

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

def text_mode_from_string(string):
    """
    Get a `TextMode` from a string.

    Args:
        string (str): The string to parse.

    Returns:
        TextMode: A text mode if `string` matched one, or None if not.
    """

    if string:
        modes = {
            'single-line': TextMode.SINGLE_LINE,
            'squish': TextMode.SQUISH,
            'wrap': TextMode.WRAP,
        }

        string = string.lower()
        if string in modes:
            return modes[string]
        else:
            return None
    else:
        return None

def colour_from_string(string):
    """
    Get an RGB tuple from an RGB hex string.

    Args:
        string (str): The RGB hex string to parse.

    Returns:
        Anchor: An RGB tuple parsed from `string`.
    """

    string = string.lstrip('#')
    stringBytes = bytearray.fromhex(string)

    return tuple(int(b) for b in stringBytes)

def bool_from_string(string):
    """
    Get a `bool` from a string.

    Args:
        string (str): The string to parse.

    Returns:
        bool: Whether `string` is 'true' or not.
    """

    return string.lower() == 'true'

def operator_from_string(string):
    """
    Get an `operator` from a string.

    Args:
        string (str): The string to parse.

    Returns:
        operator: An operator if `string` matched one, or None if not.
    """

    if string:
        operators = {
            '==': operator.eq,
            '!=': operator.ne,
            '>=': operator.ge,
            '>': operator.gt,
            '<=': operator.le,
            '<': operator.lt,
        }

        string = string.lower()
        if string in operators:
            return operators[string]
        else:
            return None
    else:
        return None

def direction_from_string(string):
    """
    Get a `Direction` from a string.

    Args:
        string (str): The string to parse.

    Returns:
        Direction: A direction if `string` matched one, or None if not.
    """

    if string:
        directions = {
            'horizontal': Direction.HORIZONTAL,
            'vertical': Direction.VERTICAL,
        }

        string = string.lower()
        if string in directions:
            return directions[string]
        else:
            return None
    else:
        return None

def gradient_type_from_string(string):
    """
    Get a `GradientType` from a string.

    Args:
        string (str): The string to parse.

    Returns:
        GradientType: A direction if `string` matched one, or None if not.
    """

    if string:
        types = {
            'linear': GradientType.LINEAR,
        }

        string = string.lower()
        if string in types:
            return types[string]
        else:
            return None
    else:
        return None

def element_from_xml(xml):
    """
    Get an `Element` from an XML element.

    Args:
        xml (ET.Element): The XML to get an `Element` from.

    Returns:
        Element: An element from `xml`.
    """

    elements = {
        'container': ContainerElement,
        'box': BoxElement,
        'texture': TextureElement,
        'text': TextElement,
        'sprite-text': SpriteTextElement,
        'switch': SwitchElement,
        'progress': ProgressElement,
    }

    special = [
        'option',
    ]

    if xml.tag in special:
        return None

    return elements[xml.tag](xml)

class Element(Drawable):
    """
    A `Drawable` that is loaded from an XML element.

    `gradient-stops` Usage:
        #colour [position] [middle], #colour2...

        position and middle are optional. position will default to dividing the
        amount of stops equally and going to the step representing its index.
        middle will default to `0.5`.

    Element Attributes:
        size: Sets both `width` and `height`, ignores `width` and `height`.

        margin: Sets all sides of `margin`, ignores the other margin attributes.

        margin-top: Sets the top value of `margin`.

        margin-bottom: Sets the top value of `margin`.

        margin-left: Sets the top value of `margin`.

        margin-right: Sets the top value of `margin`.
    """

    def __init__(self, xml):
        """
        Args:
            xml (ET.Element): The XML element to use for getting the properties
                of this element.
        """

        super(Element, self).__init__()
        self.anchor = anchor_from_string(xml.get('anchor')) or Anchor.TOP_LEFT
        self.origin = anchor_from_string(xml.get('origin')) or Anchor.TOP_LEFT
        self.x = float(xml.get('x') or 0)
        self.y = float(xml.get('y') or 0)
        self.relativeSizeAxes = axes_from_string(xml.get('relative-size-axes')) or Axes.NONE
        self.gradientType = gradient_type_from_string(xml.get('gradient-type'))
        self.gradientDirection = direction_from_string(xml.get('gradient-direction'))

        if 'size' in xml.attrib:
            s = float(xml.get('size'))
            self.size = (s, s)
        else:
            self.width = float(xml.get('width') or 0)
            self.height = float(xml.get('height') or 0)

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

        if 'gradient-stops' in xml.attrib:
            stops = xml.get('gradient-stops').split(',')
            stops = [s.strip() for s in stops]

            if len(stops) > 0:
                self.gradientStops = []

            for i in range(len(stops)):
                components = stops[i].split(' ')

                colour = colour_from_string(components[0])

                if len(components) >= 2:
                    position = float(components[1])
                else:
                    position = (1.0 / (len(stops) - 1)) * i

                if len(components) >= 3:
                    middle = float(components[2])
                else:
                    middle = 0.5

                self.gradientStops.append(GradientStop(position, colour, middle))

    def load(self, drawing):
        """
        Load this elements attributes that are dependent on a `Drawing`.

        Args:
            drawing (Drawing): The drawing to load with.
        """

        return

class ContainerElement(Element, Container):
    """
    A `Container` variant of `Element`.

    Element Usage:
        Inside of container elements you can specify child elements, such as
        below:

        <container width="400" height="400">
            <box relative-size-axes="both" size="1" colour="ffffff"/>
            ...
        </container>

    Element Attributes:
        padding: Sets all sides of `padding`, ignores the other padding
            attributes.

        padding-top: Sets the top value of `padding`.

        padding-bottom: Sets the top value of `padding`.

        padding-left: Sets the top value of `padding`.

        padding-right: Sets the top value of `padding`.
    """

    def __init__(self, xml):
        super(Container, self).__init__()
        super(ContainerElement, self).__init__(xml)

        self.masking = bool_from_string(xml.get('masking') or 'true')

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
            element = element_from_xml(node)
            if element:
                self.add(element)

    def load(self, drawing):
        for child in self.children:
            child.load(drawing)

class BoxElement(Element, Box):
    """
    A `Box` variant of `Element`.
    """

    def __init__(self, xml):
        super(Box, self).__init__()
        super(BoxElement, self).__init__(xml)

        if 'colour' in xml.attrib:
            self.colour = colour_from_string(xml.get('colour'))

class TextureElement(Element, Texture):
    """
    A `Texture` variant of `Element`.

    Element Attributes:
        file: The path to the image file for this texture to display, can be
            relative if there is no leading slash.
            Supports string formatting.
    """

    def __init__(self, xml):
        super(Texture, self).__init__()
        super(TextureElement, self).__init__(xml)

        self.file = xml.get('file')
        self.sizeToImage = bool_from_string(xml.get('size-to-image') or '')

    def load(self, drawing):
        self.file = drawing.format_string(self.file)
        self.image = Image.open(os.path.join(drawing.path, self.file))

class TextElement(Element, Text):
    """
    A `Text` variant of `Element`.

    Element Usage:
        Inside of text elements you can specify the text to display, such as
        below:

        <text ...>hello, world!</text>

        Which also supports string formatting.

    Element Attributes:
        font: The path to the font for this text to use, can be relative if
            there is no leading slash.
    """

    def __init__(self, xml):
        super(Text, self).__init__()
        super(TextElement, self).__init__(xml)

        self.relativeFontPath = xml.get('font')
        self.textSize = int(xml.get('font-size') or 0)
        self.text = xml.text
        self.mode = text_mode_from_string(xml.get('mode')) or TextMode.SINGLE_LINE
        self.lineSpacing = int(xml.get('line-spacing') or 0)

        if 'colour' in xml.attrib:
            self.textColour = colour_from_string(xml.get('colour'))

    def load(self, drawing):
        self.text = drawing.format_string(self.text)
        self.fontPath = os.path.join(drawing.path, self.relativeFontPath)

class SpriteTextElement(Element, SpriteText):
    """
    A `SpriteText` variant of `Element`.

    Element Usage:
        Inside of sprite text elements you can specify the text to display, such
        as below:

        <sprite-text ...>hello, world!</sprite-text>

        Which also supports string interpolation.

    Element Attributes:
        font: The path to the font for this text to use, can be relative if
            there is no leading slash.
    """

    def __init__(self, xml):
        super(SpriteText, self).__init__()
        super(SpriteTextElement, self).__init__(xml)

        self.relativeFontPath = xml.get('font')
        self.text = xml.text

    def load(self, drawing):
        self.text = drawing.format_string(self.text)
        self.font = SpriteFont(os.path.join(drawing.path, self.relativeFontPath))

class SwitchElement(ContainerElement):
    """
    A `ContainerElement` that hides/shows `Drawable`s depending on a value.

    Element Usage:
        Switch elements work like switch statements in programming in that a
        value is used to choose from a list of options (typically called cases).

        These options are specified by `OptionElement`s that are placed inside
        the switch element, like children in containers. Although options are
        added like children, switch elements still allow other children to be
        mixed in with the options.

        See `OptionElement` for more info on the formatting of options.

    Element Attributes:
        value: The value for this switch to switch on and compare against
            its options.
            Supports string formatting.
    """

    def __init__(self, xml):
        super(SwitchElement, self).__init__(xml)

        self.xml = xml
        self.value = xml.get('value')
        self.options = [SwitchOption(n) for n in xml.iter('option')]

    def load(self, drawing):
        super(SwitchElement, self).load(drawing)

        self.value = drawing.format_string(self.value)

        for option in self.options:
            # cast self.value and option.value to floats if they are a number so the operator works correctly

            try: sv = float(self.value)
            except: sv = self.value

            for value in option.values:
                try: ov = float(value)
                except: ov = value

                if option.operator(sv, ov):
                    # place the option at the correct index so that the elements before and after it are properly on top or below
                    children = self.xml.getchildren()
                    children = [c for c in children if (c == option.xml and c.tag == 'option') or c.tag != 'option']

                    element = element_from_xml(option.element)
                    self.add(element, children.index(option.xml))
                    element.load(drawing)

                    return

class SwitchOption:
    """
    An option for a `SwitchElement`.

    Element Usage:
        Switch options are a special type of element that wrap around a
        `DrawableElement` so a `SwitchElement` can see what values represent
        what option. Switch options only support a single element, though that
        element can then have as many children as you want. Example:

        <option ...>
            <container relative-size-axes="both" size="1">
                <box relative-size-axes="both" size="1" colour="ffffff"/>
                ...
            </container>
        </option>

        When an option is chosen by a `SwitchElement`, all the option elements
        in the switch are removed and the chosen options element is placed
        inside the switch at the same z-position as its option.

    Element Attributes:
        operator: The operator to use when comparing values against this option.
            Defaults to `==`.

        value: The value(s) that represent this option. When using multiple,
            separate the values with ", ".
    """

    def __init__(self, xml):
        """
        Args:
            xml (ET.Element): The XML element to use for getting the properties
                of this option.
        """

        self.xml = xml
        self.element = xml[0]
        self.operator = operator_from_string(xml.get('operator') or '==')
        self.values = xml.get('value').split(', ')

class ProgressElement(ContainerElement):
    """
    A `ContainerElement` that can resize based on a value.

    Element Usage:
        When a progress element sets its fill it is on a scale of 0 to 1, so you
        should typically use the same relative size axes and progress axes.

    Element Attributes:
        progress-axes: The `Axes` for this progress element to resize on.
            Defaults to `Axes.NONE`.

        value: The value for this progress to use to determine its fill percent.
            Supports string formatting.

        max: The max value that `value` can be.
            Defaults to 100.
    """

    def __init__(self, xml):
        super(ProgressElement, self).__init__(xml)

        self.axes = axes_from_string(xml.get('progress-axes') or 'none')
        self.value = xml.get('value')
        self.max = float(xml.get('max') or 100)

    def load(self, drawing):
        super(ProgressElement, self).load(drawing)

        self.value = float(drawing.format_string(self.value)) / self.max

        if self.axes & Axes.X:
            self.width = self.value
        if self.axes & Axes.Y:
            self.height = self.value

class Drawing(ContainerElement):
    """
    A special `ContainerElement` that loads and is the root node of a drawing
    file.

    Element Usage:
        <drawing width="..." height="...">
            ...
        </drawing>

        Width and height are both required and should be the only attributes
        used on a drawing element.
    """

    def __init__(self, file, values):
        """
        Args:
            file (str): The path to the file to load.

            values (any): The object to get values from when an `Element` is
                asking for values.
                When an element says it supports string formatting, it means
                that the string is formatted using these values.
        """

        if os.path.exists(file):
            tree = ET.parse(file)
            root = tree.getroot()

            if root.tag == 'drawing':
                if 'width' in root.attrib and 'height' in root.attrib:
                    super(Drawing, self).__init__(root)
                    self.path = os.path.dirname(file)
                    self.values = values

                    self.load(self)
                else:
                    raise ValueError('drawing files must specify a width and height in the root <drawing> node')
            else:
                raise ValueError('drawing files must have a root <drawing> node')
        else:
            raise ValueError('file does not exist')

    def format_string(self, string):
        """
        Format a string using `value`.

        Args:
            string (str): The string to format.

        Returns:
            str: `string` formatted with `values`.
        """

        if isinstance(self.values, dict):
            return string.format(**self.values)
        else:
            return string.format(self.values)
