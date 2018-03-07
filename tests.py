
from doodle import drawables
from doodle.drawables import Anchor, Axis

def container_test():
	container = drawables.Container(
		size=(400, 400),
		children=[
			drawables.Box(
				colour=(255, 0, 0),
				relativeSizeAxes=Axis.BOTH,
				size=(1, 1),
			),
			drawables.Container(
				anchor=Anchor.BOTTOM_RIGHT,
				origin=Anchor.BOTTOM_RIGHT,
				size=(0.5, 0.5),
				children=[
					drawables.Box(
						colour=(0, 255, 0),
						relativeSizeAxes=Axis.BOTH,
						size=(1, 1),
					),
				]
			),
		],
	)

if __name__ == '__main__':
	container_test()
