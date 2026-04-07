# HTML-in-Canvas API Specification

Complete API reference for the WICG HTML-in-Canvas proposal. Source: https://github.com/WICG/html-in-canvas

## Table of Contents

- [Complete WebIDL](#complete-webidl)
- [layoutsubtree Attribute](#layoutsubtree-attribute)
- [drawElementImage() Method](#drawelementimage-method)
- [PaintEvent](#paintevent)
- [captureElementImage()](#captureelementimage)
- [ElementImage Interface](#elementimage-interface)
- [getElementTransform()](#getelementtransform)
- [WebGL: texElementImage2D()](#webgl-texelementimage2d)
- [WebGPU: copyElementImageToTexture()](#webgpu-copyelementimagetotexture)
- [Transform Synchronization Math](#transform-synchronization-math)
- [Rendering Rules and Constraints](#rendering-rules-and-constraints)

## Complete WebIDL

```webidl
partial interface HTMLCanvasElement {
  [CEReactions, Reflect] attribute boolean layoutSubtree;
  attribute EventHandler onpaint;
  void requestPaint();
  ElementImage captureElementImage(Element element);
  DOMMatrix getElementTransform(
    (Element or ElementImage) element,
    DOMMatrix drawTransform
  );
};

partial interface OffscreenCanvas {
  DOMMatrix getElementTransform(
    (Element or ElementImage) element,
    DOMMatrix drawTransform
  );
};

interface mixin CanvasDrawElementImage {
  // Position only
  DOMMatrix drawElementImage(
    (Element or ElementImage) element,
    unrestricted double dx,
    unrestricted double dy
  );
  // Position + destination size
  DOMMatrix drawElementImage(
    (Element or ElementImage) element,
    unrestricted double dx,
    unrestricted double dy,
    unrestricted double dwidth,
    unrestricted double dheight
  );
  // Source crop + position
  DOMMatrix drawElementImage(
    (Element or ElementImage) element,
    unrestricted double sx, unrestricted double sy,
    unrestricted double swidth, unrestricted double sheight,
    unrestricted double dx, unrestricted double dy
  );
  // Source crop + destination rect (full form)
  DOMMatrix drawElementImage(
    (Element or ElementImage) element,
    unrestricted double sx, unrestricted double sy,
    unrestricted double swidth, unrestricted double sheight,
    unrestricted double dx, unrestricted double dy,
    unrestricted double dwidth, unrestricted double dheight
  );
};

CanvasRenderingContext2D includes CanvasDrawElementImage;
OffscreenCanvasRenderingContext2D includes CanvasDrawElementImage;

partial interface WebGLRenderingContext {
  void texElementImage2D(
    GLenum target,
    GLint level,
    GLint internalformat,
    GLenum format,
    GLenum type,
    (Element or ElementImage) element
  );
};

partial interface GPUQueue {
  void copyElementImageToTexture(
    (Element or ElementImage) source,
    GPUImageCopyTextureTagged destination
  );
};

[Exposed=Window]
interface PaintEvent : Event {
  constructor(DOMString type, optional PaintEventInit eventInitDict);
  readonly attribute FrozenArray<Element> changedElements;
};

dictionary PaintEventInit : EventInit {
  sequence<Element> changedElements = [];
};

[Exposed=(Window,Worker), Transferable]
interface ElementImage {
  readonly attribute unsigned long width;
  readonly attribute unsigned long height;
  undefined close();
};
```

## layoutsubtree Attribute

HTML boolean attribute on `<canvas>` elements. Enables canvas children to participate in layout and hit testing.

**Effects when set:**
- Direct children receive stacking context
- Children become containing blocks for their descendants
- Children gain paint containment
- Children render invisibly until explicitly drawn via `drawElementImage()`
- Children remain interactive (clickable, focusable, typeable)

**Usage:**
```html
<canvas layoutsubtree>
  <div id="content">This is laid out but invisible until drawn</div>
</canvas>
```

JavaScript property: `canvas.layoutSubtree` (camelCase, boolean).

## drawElementImage() Method

Draws a canvas child element into the canvas context. Returns a `DOMMatrix` for transform synchronization.

**Overloads:**

| Signature | Description |
|---|---|
| `drawElementImage(element, dx, dy)` | Draw at position |
| `drawElementImage(element, dx, dy, dw, dh)` | Draw at position with destination size |
| `drawElementImage(element, sx, sy, sw, sh, dx, dy)` | Source crop + position |
| `drawElementImage(element, sx, sy, sw, sh, dx, dy, dw, dh)` | Full: source crop + destination rect |

**Parameters:**
- `element`: An `Element` (direct child of canvas) or `ElementImage` (captured snapshot)
- `sx, sy, sw, sh`: Source rectangle (crop from element)
- `dx, dy`: Destination position on canvas
- `dw, dh`: Destination size (scales the element)

**Return value:** `DOMMatrix` — apply to element's CSS `transform` to synchronize DOM position with rendered position for hit testing.

**Behavior:**
- Records a snapshot of rendering prior to the paint event
- During paint event: draws current frame
- Outside paint event: uses previous frame snapshot
- Throws exception if called before initial snapshot recorded
- Canvas transformation matrix (translate, rotate, scale) applies to drawing
- CSS transforms on source elements are ignored for drawing purposes
- Overflowing content is clipped to element's border box

**Requirements (throws if violated):**
- `layoutsubtree` must be set on `<canvas>` in the most recent rendering update
- Element must be a direct child of the canvas in the most recent rendering update
- Element must have generated boxes (not `display: none`)

## PaintEvent

Fires on canvas elements when rendering of canvas children changes. Fires after intersection observer steps during update-the-rendering.

**Properties:**
- `changedElements`: `FrozenArray<Element>` — list of child elements whose rendering changed

**Characteristics:**
- Fires once per frame (not in a loop like `requestAnimationFrame`)
- CSS transform changes do NOT trigger the event
- Canvas drawing commands appear in the current frame
- DOM changes appear in the subsequent frame

**`requestPaint()`:** Forces a paint event to fire in the next frame, even if no child rendering changed. Call after ResizeObserver updates canvas dimensions.

```js
canvas.onpaint = (event) => {
  ctx.reset();
  const transform = ctx.drawElementImage(child, x, y);
  child.style.transform = transform.toString();
};
canvas.requestPaint();
```

## captureElementImage()

```js
ElementImage captureElementImage(Element element)
```

Creates a transferable snapshot of an element's rendering. Use with `OffscreenCanvas` in workers.

**Workflow:**
1. Capture on main thread: `const img = canvas.captureElementImage(element)`
2. Transfer to worker: `worker.postMessage({ elementImage: img }, [img])`
3. Draw in worker: `ctx.drawElementImage(img, x, y)`
4. Get transform in worker: `offscreen.getElementTransform(img, drawTransform)`
5. Send transform back: `self.postMessage({ transform })`
6. Apply on main thread: `element.style.transform = transform.toString()`

## ElementImage Interface

Transferable snapshot of element rendering. Can be used anywhere `Element` is accepted in drawing APIs.

**Properties:**
- `width`: `unsigned long` — pixel width of captured image
- `height`: `unsigned long` — pixel height of captured image

**Methods:**
- `close()`: Release the snapshot resources

**Exposed:** `Window` and `Worker` contexts. Implements `Transferable`.

## getElementTransform()

```js
DOMMatrix getElementTransform(
  (Element or ElementImage) element,
  DOMMatrix drawTransform
)
```

Available on `HTMLCanvasElement` and `OffscreenCanvas`. Computes the CSS transform to apply to a DOM element so its hit-test region aligns with its rendered position on the canvas.

**Parameters:**
- `element`: The element or captured image
- `drawTransform`: The canvas transformation matrix that was active when drawing

**Returns:** `DOMMatrix` to apply as CSS transform.

## WebGL: texElementImage2D()

```js
gl.texElementImage2D(
  gl.TEXTURE_2D,    // target
  0,                // level
  gl.RGBA,          // internalformat
  gl.RGBA,          // format
  gl.UNSIGNED_BYTE, // type
  element           // Element or ElementImage
);
```

Uploads an element's rendering as a WebGL texture. Use like `texImage2D` but with a DOM element. The element's rendered content becomes a texture that can be applied to 3D geometry.

**Important:** For WebGL, elements should typically be marked `inert` since interaction happens in 3D space, not DOM space.

## WebGPU: copyElementImageToTexture()

```js
device.queue.copyElementImageToTexture(
  element,          // Element or ElementImage (source)
  { texture: tex }  // GPUImageCopyTextureTagged (destination)
);
```

Copies element rendering to a WebGPU texture.

## Transform Synchronization Math

The returned `DOMMatrix` from `drawElementImage()` accounts for the mapping between canvas grid coordinates and CSS pixel coordinates. The formula:

```
T = T_origin^-1 * S_css_to_grid^-1 * T_draw * S_css_to_grid * T_origin
```

Where:
- `T_draw`: The canvas CTM at the time of drawing
- `T_origin`: Translation by the element's computed `transform-origin`
- `S_css_to_grid`: Scaling from CSS pixels to canvas grid pixels (typically `devicePixelRatio`)

In practice, just call `.toString()` on the returned matrix and assign to `element.style.transform`.

## Rendering Rules and Constraints

**What gets rendered:**
- Full CSS box model (borders, padding, backgrounds)
- Text with all CSS text properties (font, direction, writing-mode, etc.)
- Inline images and SVG
- Form controls (inputs, buttons, checkboxes, etc.)
- Emoji and international text (RTL, vertical)

**What gets clipped/excluded:**
- Content overflowing the element's border box is clipped
- CSS transforms on the source element are ignored for drawing
- Cross-origin embedded content (iframes, cross-origin images, URL references)

**Coordinate system:**
- Canvas drawing uses grid pixel coordinates (affected by `devicePixelRatio`)
- Use `ResizeObserver` with `device-pixel-content-box` to keep canvas dimensions in sync
- The returned transform bridges CSS pixels and canvas grid pixels automatically

**Frame timing:**
- `drawElementImage()` during paint event → draws current frame content
- `drawElementImage()` outside paint event → draws previous frame snapshot
- DOM changes made during paint event → visible next frame
- Canvas drawing during paint event → visible current frame
