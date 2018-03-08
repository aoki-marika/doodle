
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

	container.render().save('container_test.png')

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

	container.render().save('margin_padding_test.png')

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

	container.render().save('masking_test.png')

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
	container.render().save('component_test.png')

if __name__ == '__main__':
	container_test()
	margin_padding_test()
	masking_test()
	component_test()
