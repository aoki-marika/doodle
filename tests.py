
from doodle import Drawable, Container, Box, Texture, Text, SpriteText, SpriteFont, Anchor, Axes, Drawing, TextMode, GradientType, GradientPoint, draw_gradient

from PIL import Image

def container_test():
    container = Container(
        size=(400, 400),
        children=[
            Box(
                relativeSizeAxes=Axes.BOTH,
                size=(1, 1),
                colour=(255, 0, 0),
            ),
            Box(
                relativeSizeAxes=Axes.Y,
                width=50,
                height=1,
                colour=(255, 255, 0),
            ),
            Box(
                relativeSizeAxes=Axes.X,
                width=1,
                height=50,
                colour=(0, 255, 225),
            ),
            Box(
                anchor=Anchor.CENTER,
                origin=Anchor.CENTER,
                relativeSizeAxes=Axes.BOTH,
                size=(0.25, 0.25),
                colour=(255, 255, 255),
            ),
            Container(
                anchor=Anchor.BOTTOM_RIGHT,
                origin=Anchor.BOTTOM_RIGHT,
                relativeSizeAxes=Axes.BOTH,
                size=(0.5, 0.5),
                children=[
                    Box(
                        relativeSizeAxes=Axes.BOTH,
                        size=(1, 1),
                        colour=(0, 255, 0),
                    ),
                    Box(
                        origin=Anchor.CENTER,
                        relativeSizeAxes = Axes.BOTH,
                        size=(0.5, 0.5),
                        colour=(0, 0, 255),
                    )
                ]
            ),
            Box(
                anchor=Anchor.BOTTOM_RIGHT,
                origin=Anchor.CENTER,
                relativeSizeAxes=Axes.BOTH,
                size=(0.25, 0.25),
                colour=(255, 0, 255),
            ),
        ],
    )

    container.render().save('tests/container_test.png')

def margin_padding_test():
    container = Container(
        size=(400, 400),
        padding=(10, 20, 30, 40),
        children=[
            Box(
                relativeSizeAxes=Axes.BOTH,
                size=(1, 1),
                colour=(255, 0, 0),
            ),
            Container(
                relativeSizeAxes=Axes.BOTH,
                size=(1, 1),
                padding=(10, 20, 30, 40),
                children=[
                    Box(
                        relativeSizeAxes=Axes.Y,
                        size=(50, 1),
                        colour=(0, 255, 0),
                    ),
                    Box(
                        relativeSizeAxes=Axes.X,
                        size=(1, 50),
                        colour=(0, 0, 255),
                    ),
                ],
            ),
            Container(
                relativeSizeAxes=Axes.BOTH,
                size=(1, 1),
                padding=(80, 20, 100, 40),
                children=[
                    Box(
                        relativeSizeAxes=Axes.BOTH,
                        size=(1, 1),
                        colour=(255, 255, 0),
                    ),
                    Container(
                        size=(60, 100),
                        margin=(20, 0, 20, 0),
                        children=[
                            Box(
                                relativeSizeAxes=Axes.BOTH,
                                size=(1, 1),
                                colour=(0, 255, 255),
                            ),
                        ],
                    ),
                    Container(
                        anchor=Anchor.TOP_RIGHT,
                        origin=Anchor.TOP_RIGHT,
                        size=(60, 100),
                        margin=(20, 0, 0, 20),
                        children=[
                            Box(
                                relativeSizeAxes=Axes.BOTH,
                                size=(1, 1),
                                colour=(0, 255, 255),
                            ),
                        ],
                    ),
                    Container(
                        anchor=Anchor.BOTTOM_LEFT,
                        origin=Anchor.BOTTOM_LEFT,
                        size=(60, 100),
                        margin=(0, 20, 20, 0),
                        children=[
                            Box(
                                relativeSizeAxes=Axes.BOTH,
                                size=(1, 1),
                                colour=(0, 255, 255),
                            ),
                        ],
                    ),
                    Container(
                        anchor=Anchor.BOTTOM_RIGHT,
                        origin=Anchor.BOTTOM_RIGHT,
                        size=(60, 100),
                        margin=(0, 20, 0, 20),
                        children=[
                            Box(
                                relativeSizeAxes=Axes.BOTH,
                                size=(1, 1),
                                colour=(0, 255, 255),
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    container.render().save('tests/margin_padding_test.png')

def masking_test():
    container = Container(
        size=(400, 400),
        children = [
            Container(
                anchor=Anchor.CENTER,
                origin=Anchor.CENTER,
                size=(100, 100),
                masking=False,
                children=[
                    Box(
                        anchor=Anchor.CENTER,
                        origin=Anchor.CENTER,
                        relativeSizeAxes=Axes.BOTH,
                        size=(1.5, 1.5),
                        colour=(0, 0, 255),
                    ),
                    Box(
                        relativeSizeAxes=Axes.BOTH,
                        size=(1, 1),
                        colour=(255, 0, 0),
                    ),
                    Container(
                        relativeSizeAxes=Axes.BOTH,
                        size=(1, 1),
                        children=[
                            Box(
                                anchor=Anchor.CENTER,
                                origin=Anchor.CENTER,
                                relativeSizeAxes=Axes.X,
                                width=2,
                                height=20,
                                colour=(0, 255, 0),
                            ),
                        ],
                    ),
                    Box(
                        anchor=Anchor.CENTER,
                        origin=Anchor.CENTER,
                        relativeSizeAxes=Axes.Y,
                        width=20,
                        height=2,
                        colour=(0, 255, 0),
                    ),
                ],
            ),
        ],
    )

    container.render().save('tests/masking_test.png')

class ProgressBar(Container):
    def __init__(self, **kwargs):
        self.fill = Container(
            relativeSizeAxes=Axes.BOTH,
            height=1,
            masking=False,
            children=[
                # fill
                Box(
                    relativeSizeAxes=Axes.BOTH,
                    size=(1, 1),
                    colour=(255, 0, 0),
                ),
                # indicator
                Box(
                    anchor=Anchor.CENTER_RIGHT,
                    origin=Anchor.CENTER_RIGHT,
                    width=10,
                    height=80,
                    colour=(0, 0, 255),
                ),
            ],
        )

        super(ProgressBar, self).__init__(
            masking=False,
            children=[
                Box(
                    relativeSizeAxes=Axes.BOTH,
                    size=(1, 1),
                    colour=(0, 0, 0),
                ),
                self.fill,
            ],
            **kwargs,
        )

    @property
    def progress(self):
        return self.fill.width

    @progress.setter
    def progress(self, value):
        self.fill.width = value

def component_test():
    progress = ProgressBar(
        anchor=Anchor.CENTER,
        origin=Anchor.CENTER,
        relativeSizeAxes=Axes.X,
        width=1,
        height=20,
    )

    container = Container(
        width=200,
        height=100,
        children=[
            progress,
        ],
    )

    progress.progress = 0.3
    container.render().save('tests/component_test.png')

def texture_test():
    image = Image.open('tests/assets/lenna.png')

    container = Container(
        size=(400, 400),
        children=[
            Texture(
                anchor=Anchor.CENTER,
                origin=Anchor.CENTER,
                image=image,
                sizeToImage=True,
            ),
            Texture(
                relativeSizeAxes=Axes.BOTH,
                width=0.5,
                height=1,
                image=image,
            ),
            Texture(
                anchor=Anchor.BOTTOM_RIGHT,
                origin=Anchor.BOTTOM_RIGHT,
                relativeSizeAxes=Axes.BOTH,
                size=(0.4, 0.4),
                image=image,
                margin=(0, 20, 0, 20),
            ),
        ],
    )

    container.render().save('tests/texture_test.png')

def text_test():
    font = 'tests/assets/concert-one.ttf'

    container = Container(
        size=(400, 400),
        padding=(20, 20, 20, 20),
        children=[
            Box(
                relativeSizeAxes=Axes.BOTH,
                size=(1, 1),
                colour=(0, 0, 0),
            ),
            Container(
                size=(150, 40),
                children=[
                    Box(
                        relativeSizeAxes=Axes.BOTH,
                        size=(1, 1),
                        colour=(255, 255, 255),
                    ),
                    Text(
                        anchor=Anchor.TOP_CENTER,
                        origin=Anchor.TOP_CENTER,
                        relativeSizeAxes=Axes.X,
                        width=1,
                        fontPath=font,
                        textColour=(255, 0, 0),
                        textSize=15,
                        text='top left squish to fit, squuuuish',
                        mode=TextMode.SQUISH,
                    ),
                    Text(
                        anchor=Anchor.BOTTOM_CENTER,
                        origin=Anchor.BOTTOM_CENTER,
                        relativeSizeAxes=Axes.X,
                        width=1,
                        fontPath=font,
                        textColour=(255, 0, 0),
                        textSize=15,
                        text='top left squish fits',
                        mode=TextMode.SQUISH,
                    ),
                ],
            ),
            Container(
                anchor=Anchor.TOP_RIGHT,
                origin=Anchor.TOP_RIGHT,
                size=(150, 150),
                children=[
                    Box(
                        relativeSizeAxes=Axes.BOTH,
                        size=(1, 1),
                        colour=(255, 255, 255),
                    ),
                    Text(
                        anchor=Anchor.CENTER,
                        origin=Anchor.CENTER,
                        relativeSizeAxes=Axes.BOTH,
                        size=(1, 1),
                        fontPath=font,
                        textColour=(255, 0, 0),
                        textSize=10,
                        text='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. centered wrap. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
                        mode=TextMode.WRAP,
                        lineSpacing=5,
                    ),
                ],
            ),
            Text(
                anchor=Anchor.BOTTOM_LEFT,
                origin=Anchor.BOTTOM_LEFT,
                fontPath=font,
                textColour=(0, 0, 255),
                textSize=16,
                text='bottom left',
            ),
            Text(
                anchor=Anchor.BOTTOM_RIGHT,
                origin=Anchor.BOTTOM_RIGHT,
                fontPath=font,
                textColour=(255, 255, 0),
                textSize=14,
                text='bottom right',
            ),
            Text(
                anchor=Anchor.CENTER,
                origin=Anchor.CENTER,
                fontPath=font,
                textColour=(0, 255, 255),
                textSize=30,
                text='hello, world!',
            ),
        ],
    )

    container.render().save('tests/text_test.png')

def sprite_text_test():
    font = SpriteFont('tests/assets/image-font')

    container = Container(
        size=(400, 400),
        padding=(20, 20, 20, 20),
        children=[
            Box(
                relativeSizeAxes=Axes.BOTH,
                size=(1, 1),
                colour=(0, 0, 0),
            ),
            SpriteText(
                font=font,
                text='0/0',
            ),
            SpriteText(
                anchor=Anchor.TOP_RIGHT,
                origin=Anchor.TOP_RIGHT,
                font=font,
                text='60/0',
            ),
            SpriteText(
                anchor=Anchor.CENTER,
                origin=Anchor.CENTER,
                font=font,
                text='50/60',
            ),
            SpriteText(
                anchor=Anchor.BOTTOM_LEFT,
                origin=Anchor.BOTTOM_LEFT,
                font=font,
                text='0/60',
            ),
            SpriteText(
                anchor=Anchor.BOTTOM_RIGHT,
                origin=Anchor.BOTTOM_RIGHT,
                font=font,
                text='60/50',
            ),
        ],
    )

    container.render().save('tests/sprite_text_test.png')

def drawing_test():
    values = {
        'key_one': {
            'value_one': 1,
            'value_two': 2,
        },
        'key_two': {
            'value_three': 3,
            'value_four': 4,
        },
        'value_five': 5,
        'switch_value': 80,
    }

    drawing = Drawing('tests/assets/drawing.xml', values)
    drawing.render().save('tests/drawing_test.png')

def gradient_test():
    points = [
        GradientPoint(0, (255, 0, 0), 0.6),
        GradientPoint(0.25, (0, 255, 0), 0.25),
        GradientPoint(0.75, (0, 0, 255), 0.25),
        GradientPoint(1, (0, 0, 0)),
    ]

    draw_gradient(400, 400, GradientType.LINEAR, points, 0).save('tests/gradient_test.png')

if __name__ == '__main__':
    # container_test()
    # margin_padding_test()
    # masking_test()
    # component_test()
    # texture_test()
    # text_test()
    # sprite_text_test()
    # drawing_test()
    gradient_test()
