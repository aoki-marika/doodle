
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
			Box(
				relativeSizeAxes=Axes.Y,
				size=(50, 1),
				colour=(0, 255, 0),
				margin=(10, 20, 30, 40)
			),
			Box(
				relativeSizeAxes=Axes.X,
				size=(1, 50),
				colour=(0, 0, 255),
				margin=(10, 20, 30, 40)
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

	container.render().save('margin_padding_test.png')

if __name__ == '__main__':
	container_test()
	# autosize_test()
	margin_padding_test()
