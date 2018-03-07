
from doodle import Drawable, Container, Box, Anchor, Axes

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
						anchor=Anchor.CENTER,
						relativeSizeAxes = Axes.BOTH,
						size=(0.5, 0.5),
						colour=(0, 0, 255),
					)
				]
			),
			Box(
				anchor=Anchor.CENTER,
				origin=Anchor.BOTTOM_RIGHT,
				relativeSizeAxes=Axes.BOTH,
				size=(0.25, 0.25),
				colour=(255, 0, 255),
			),
		],
	)

	container.render().save('container_test.png')

def autosize_test():
	container = Container(
		size=(400, 400),
		children=[
			Container(
				autoSizeAxes=Axes.X,
				relativeSizeAxes=Axes.Y,
				height=1,
				children=[
					Box(
						relativeSizeAxes=Axes.BOTH,
						size=(1, 1),
						colour=(255, 255, 255),
					),
					Box(
						size=(50, 50),
						colour=(255, 0, 0),
					),
					Box(
						size=(100, 50),
						y=50,
						colour=(0, 255, 0),
					),
					Box(
						size=(150, 50),
						y=100,
						colour=(0, 0, 255),
					),
				],
			),
			Container(
				anchor=Anchor.TOP_RIGHT,
				origin=Anchor.TOP_RIGHT,
				relativeSizeAxes=Axes.X,
				autoSizeAxes=Axes.Y,
				width=0.5,
				children=[
					Box(
						anchor=Anchor.TOP_RIGHT,
						origin=Anchor.TOP_RIGHT,
						relativeSizeAxes=Axes.BOTH,
						size=(1, 1),
						colour=(255, 255, 255),
					),
					Box(
						anchor=Anchor.TOP_RIGHT,
						origin=Anchor.TOP_RIGHT,
						size=(50, 50),
						colour=(255, 0, 0),
					),
					Box(
						anchor=Anchor.TOP_RIGHT,
						origin=Anchor.TOP_RIGHT,
						size=(100, 50),
						y=100,
						colour=(0, 255, 0),
					),
					Box(
						anchor=Anchor.TOP_RIGHT,
						origin=Anchor.TOP_RIGHT,
						size=(150, 50),
						y=200,
						colour=(0, 0, 255),
					),
				],
			),
		],
	)

	container.render().save('autosize_test.png')

if __name__ == '__main__':
	container_test()
	# autosize_test()
