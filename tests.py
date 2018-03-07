
from doodle import drawables
from doodle.drawables import Anchor, Axis

def container_test():
	container = drawables.Container(
		size=(400, 400),
		children=[
			drawables.Box(
				relativeSizeAxis=Axis.BOTH,
				size=(1, 1),
				colour=(255, 0, 0),
			),
			drawables.Box(
				relativeSizeAxis=Axis.Y,
				width=50,
				height=1,
				colour=(255, 255, 0),
			),
			drawables.Box(
				relativeSizeAxis=Axis.X,
				width=1,
				height=50,
				colour=(0, 255, 225),
			),
			drawables.Box(
				anchor=Anchor.CENTER,
				origin=Anchor.CENTER,
				relativeSizeAxis=Axis.BOTH,
				size=(0.25, 0.25),
				colour=(255, 255, 255),
			),
			drawables.Container(
				anchor=Anchor.BOTTOM_RIGHT,
				origin=Anchor.BOTTOM_RIGHT,
				relativeSizeAxis=Axis.BOTH,
				size=(0.5, 0.5),
				children=[
					drawables.Box(
						relativeSizeAxis=Axis.BOTH,
						size=(1, 1),
						colour=(0, 255, 0),
					),
					drawables.Box(
						anchor=Anchor.CENTER,
						relativeSizeAxis = Axis.BOTH,
						size=(0.5, 0.5),
						colour=(0, 0, 255),
					)
				]
			),
		],
	)

	container.render().save('container_test.png')

if __name__ == '__main__':
	container_test()
