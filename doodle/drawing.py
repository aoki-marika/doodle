
import operator
import os

import xml.etree.ElementTree as ET

from doodle import Drawable, Container, Box, Texture, Text, SpriteText, Anchor, Axes, TextMode
from PIL import Image

def anchor_from_string(string):
    """
    Get an <Anchor> from a string.

    :param string: The string to parse.
    :returns: An <Anchor> if <string> matched one, or <None> if not.
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
    Get an <Axes> from a string.

    :param string: The string to parse.
    :returns: An <Axes> if <string> matched one, or <None> if not.
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
    Get a <TextMode> from a string.

    :param string: The string to parse.
    :returns: A <TextMode> if <string> matched one, or <None> if not.
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
    Get an RGB tuple from an RGB hex.

    :param string: The RGB hex to parse.
    :returns: An RGB tuple parsed from <string>.
    """

    string = string.lstrip('#')
    return tuple(int(string[i : i + 2], 16) for i in (0, 2, 4))

def bool_from_string(string):
    """
    Get a <Boolean> from a string.

    :param string: The string to parse.
    :returns: Whether <string> is 'true' or not.
    """

    return string.lower() == 'true'

def operator_from_string(string):
    """
    Get an <operator> from a string.

    :param string: The string to parse.
    :returns: The <operator> in <string>.
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

def element_from_xml(xml):
    """
    Get an <Element> from an XML node.

    :param xml: The XML to get an <Element> for.
    :returns: An <Element> from <xml>.
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
    A <Drawable> that is loaded from an XML node.
    """

    def __init__(self, xml):
        """
        :param xml: The XML node to parse to get the properties of this element.
        """

        super(Element, self).__init__()
        self.anchor = anchor_from_string(xml.get('anchor')) or Anchor.TOP_LEFT
        self.origin = anchor_from_string(xml.get('origin')) or Anchor.TOP_LEFT
        self.x = float(xml.get('x') or 0)
        self.y = float(xml.get('y') or 0)
        self.relativeSizeAxes = axes_from_string(xml.get('relative-size-axes')) or Axes.NONE

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

    def load(self, drawing):
        """
        Load this elements attributes that are dependant on a <Drawing>.

        :param drawing: The <Drawing> to load with.
        """

        return

class ContainerElement(Element, Container):
    """
    A <Container> variant of <Element>.
    """

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
            element = element_from_xml(node)
            if element:
                self.add(element)

    def load(self, drawing):
        for child in self.children:
            child.load(drawing)

class BoxElement(Element, Box):
    """
    A <Box> variant of <Element>.
    """

    def __init__(self, xml):
        super(Box, self).__init__()
        super(BoxElement, self).__init__(xml)

        self.colour = colour_from_string(xml.get('colour') or '')

class TextureElement(Element, Texture):
    """
    A <Texture> variant of <Element>.
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
    A <Text> variant of <Element>.
    """

    def __init__(self, xml):
        super(Text, self).__init__()
        super(TextElement, self).__init__(xml)

        self.relativeFontPath = xml.get('font')
        self.textColour = colour_from_string(xml.get('colour') or '')
        self.textSize = int(xml.get('font-size') or 0)
        self.text = xml.text
        self.mode = text_mode_from_string(xml.get('mode')) or TextMode.SINGLE_LINE
        self.lineSpacing = int(xml.get('line-spacing') or 0)

    def load(self, drawing):
        self.text = drawing.format_string(self.text)
        self.fontPath = os.path.join(drawing.path, self.relativeFontPath)

class SpriteTextElement(Element, SpriteText):
    """
    A <SpriteText> variant of <Element>.
    """

    def __init__(self, xml):
        super(SpriteText, self).__init__()
        super(SpriteTextElement, self).__init__(xml)

        self.relativeFontPath = xml.get('font')
        self.text = xml.text

    def load(self, drawing):
        self.text = drawing.format_string(self.text)
        self.fontPath = os.path.join(drawing.path, self.relativeFontPath)

class SwitchElement(ContainerElement):
    """
    A <ContainerElement> that hides/shows <Drawable>s depending on a value.
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
    An option for a <SwitchElement>.
    """

    def __init__(self, xml):
        self.xml = xml
        self.element = xml[0]
        self.operator = operator_from_string(xml.get('operator') or '==')
        self.values = xml.get('value').split(', ')

class ProgressElement(ContainerElement):
    """
    A <ContainerElement> that can resize based on a value.
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
    A special <ContainerElement> that loads a file.
    """

    def __init__(self, file, values):
        """
        :param file: The path to the file to load.
        :param values: The object to get values from when an <Element> is asking for values.
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
        if isinstance(self.values, dict):
            return string.format(**self.values)
        else:
            return string.format(self.values)
