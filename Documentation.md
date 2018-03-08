## Drawable

The base class for anything that can be drawn onto an `Image`.

**parent**: The `Container` that contains this `Drawable`.

**size**: The size of this `Drawable` (`width`, `height`).

  * The `width` and `height` properties can be used to easily set just the `width` or `height` value of `size`.

**position**: The position (in pixels) of this `Drawable`, relative to `anchor`, `origin` and `parent`.

  * The `x` and `y` properties can be used to easily set just the `x` or `y` value of `position `.

**anchor**: The point in `parent` that this `Drawable` is anchored to.

**origin**: The point in this `Drawable` that `anchor` should center on.

**relativeSizeAxes**: Set `width` and or `height` to be a percentage of `parent`'s size.

**margin**: The margin of each side of this `Drawable` (`top`, `bottom`, `left`, `right`).

**draw_size**: The size of this `Drawable` to use when drawing.

**draw_position**: The position of `draw_size`, relative to `parent`.

**layout_size**: The size of this `Drawable` to use when calculating layout.

**layout_position**: The position of `layout_size`, relative to `parent`.

## Container

A type of `Drawable` that can hold other `Drawable`s inside of it.

**children**: The `Drawable`s that this `Container` contains.

**padding**: The padding of each side of this `Container` (`top`, `bottom`, `left`, `right`).

**masking**: Whether or not this `Container` should mask its children.

**children_size**: The size of the box that `children` are placed relative to.

**children_position**: The position of `children_size`, relative to `parent`.

**render_size**: A special size that's used when `masking` is disabled so that all the children can draw on the same size canvas.

**render_position**: The position of `render_size`, relative to `parent`.

## Box

A type of `Drawable` that draws a coloured box.

**colour**: The colour of this `Box`.

## Texture

A type of `Drawable` that draws a Pillow `Image`.

**image**: The `Image` for this `Texture` to draw.

**sizeToImage**: Whether or not this `Texture` should automatically resize to fit its image.

## Text

A type of `Drawable` that can draw text.

***Note***: Size related properties should not be set on `Text` elements, as they automatically resize to fit their text.

**fontPath**: The path to the TTF that this `Text` should draw with.

**textColour**: The colour that this `Text` should draw with.

**textSize**: The height in pixels of the font that this `Text` should draw with.

**text**: The string for this `Text` to draw.
