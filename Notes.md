## Drawable

The base class for any object that can be drawn onto an `Image`.

**Parent**: The `Container` that contains this `Drawable`.

**Size**: The size of this `Drawable` (`width`, `height`).

**Position**: The position (in pixels) of this `Drawable`, relative to `parent` and `anchor`/`origin`.

**Anchor**: The point in the parent that this `Drawable` is anchored to.

**Origin**: The point in this `Drawable` that `anchor` should center on.

**RelativeSizeAxes**: Set `width` and or `height` to be a percentage of `parent`'s size.

**Margin**: The margin of each side of this `Drawable` (`top`, `bottom`, `left`, `right`).

  * **Note**: When using `relativeSizeAxes` with `margin`, `margin` is removed from `parent`'s size when calculating the size of the `Drawable`.

**DrawSize**: The final size of this `Drawable`, with `relativeSizeAxes` applied.

**DrawPosition**: The final position of this `Drawable`, with `anchor` and `origin` applied.

**LayoutSize** and **LayoutPosition** : `draw_position` and `draw_size` with `margin` applied.

## Container

A type of `Drawable` that can hold other `Drawable`s inside of it.

**Children**: The `Drawable`s that this `Container` contains.

**Padding**: The padding of each side of this `Container` (`top`, `bottom`, `left`, `right`).

**AutoSizeAxes**: Set `width` and or `height` to automatically resize to fit this `Container`'s `children`.

**DrawSize**: The final size of this `Drawable`, with `relativeSizeAxes` and `autoSizeAxes` applied.

**ChildrenSize**: The final size of the area to position `children` relative to.

**ChildrenPosition**: The final position of the area to position `children` relative to.