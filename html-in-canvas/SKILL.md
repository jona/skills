---
name: html-in-canvas
description: "Implement the WICG HTML-in-Canvas API for rendering HTML/CSS content into 2D canvas, WebGL, and WebGPU contexts with full interactivity, accessibility, and transform synchronization. Use when: (1) drawing HTML elements into a canvas with drawElementImage(), (2) rendering styled text, forms, or rich content in canvas, (3) using layoutsubtree attribute, (4) handling paint events for canvas child elements, (5) using texElementImage2D() for WebGL HTML textures, (6) using copyElementImageToTexture() for WebGPU, (7) transferring element snapshots to OffscreenCanvas workers with captureElementImage(), (8) synchronizing DOM hit-test transforms with canvas-rendered positions, (9) building accessible canvas applications with ARIA and drawFocusIfNeeded(), or (10) any code involving the html-in-canvas or canvas-draw-element Chrome flag APIs."
---

# HTML-in-Canvas

WICG proposal for rendering HTML/CSS content into canvas contexts. Spec: https://github.com/WICG/html-in-canvas

**Status:** Behind `chrome://flags/#canvas-draw-element` in Chromium. Living specification — API surface may change.

## Core Concepts

Three primitives work together:

1. **`layoutsubtree` attribute** on `<canvas>` — opts children into layout/hit-testing while keeping them visually hidden until drawn
2. **`drawElementImage()`** — draws a child element into the canvas, returns a `DOMMatrix` for transform synchronization
3. **`paint` event** — fires when child element rendering changes, once per frame

## Minimal Implementation Pattern

Every implementation requires these three pieces:

```html
<canvas id="c" layoutsubtree>
  <div id="el">Content here</div>
</canvas>
<script>
  const ctx = c.getContext('2d');

  // 1. Paint handler: draw + sync transforms
  c.onpaint = () => {
    ctx.reset();
    const t = ctx.drawElementImage(el, 0, 0);
    el.style.transform = t.toString();
  };

  // 2. DPI-correct sizing
  new ResizeObserver(([e]) => {
    const b = e.devicePixelContentBoxSize[0];
    c.width = b.inlineSize;
    c.height = b.blockSize;
  }).observe(c, { box: 'device-pixel-content-box' });

  // 3. Trigger initial paint
  c.requestPaint();
</script>
```

## Deciding Which Context to Use

- **2D Canvas** (`getContext('2d')`) — Use `drawElementImage()`. Elements remain interactive (forms, links, buttons work). Best for charts, styled text, HUDs, composited effects.
- **WebGL** (`getContext('webgl2')`) — Use `texElementImage2D()`. Mark children `inert` since interaction is in 3D space. Best for HTML as 3D textures (e.g., cube faces, billboards).
- **WebGPU** — Use `device.queue.copyElementImageToTexture()`. Same `inert` pattern as WebGL.
- **OffscreenCanvas (Worker)** — Use `captureElementImage()` on main thread, transfer `ElementImage` to worker, draw with `drawElementImage()` on worker context.

## Critical Implementation Details

### Transform Synchronization is Required

`drawElementImage()` returns a `DOMMatrix`. Apply it to the element's CSS `transform` so the DOM hit-test region aligns with the visual position on canvas. Without this, clicks/focus land in the wrong place.

```js
const transform = ctx.drawElementImage(el, x, y);
el.style.transform = transform.toString();
```

### Canvas Transforms Apply, CSS Transforms Don't

Canvas CTM (translate, rotate, scale, setTransform) affects drawing. CSS transforms on the source element are ignored for rendering — but the returned `DOMMatrix` accounts for them for hit-testing.

### Frame Timing

- During `paint` event: `drawElementImage()` renders current frame
- Outside `paint` event: renders previous frame snapshot
- DOM changes in `paint` handler appear next frame
- Canvas drawing in `paint` handler appears current frame
- `requestPaint()` forces event even if nothing changed

### Element Requirements (Throws if Violated)

- `layoutsubtree` must be set on the canvas
- Element must be a **direct child** of the canvas
- Element must generate boxes (not `display: none`)

### Overflowing Content

Content overflowing the element's border box is clipped. Set explicit `width` on child elements to control text wrapping and layout bounds.

## Accessibility

- Use ARIA roles on canvas children (`role="list"`, `role="listitem"`, `aria-label`)
- Add `tabindex="0"` for keyboard focus
- Use `drawFocusIfNeeded(path, element)` to draw visible focus rings
- Canvas fallback content with `layoutsubtree` maintains screen reader correspondence

## Security Constraints

Cross-origin content, visited link styles, spellcheck markers, and autofill previews are excluded from rendering. See [references/security-privacy.md](references/security-privacy.md) for the complete security model.

## Reference Files

- **[references/api-spec.md](references/api-spec.md)** — Complete WebIDL, all method signatures, all overloads, parameter details, return types, rendering rules, coordinate system details
- **[references/examples.md](references/examples.md)** — Full working examples: rotated text, interactive forms, accessible pie chart, WebGL 3D cube, OffscreenCanvas worker pattern, common recipes
- **[references/security-privacy.md](references/security-privacy.md)** — Security model, excluded/allowed rendering data, developer security implications
