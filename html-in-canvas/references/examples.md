# HTML-in-Canvas Examples

Complete working examples from the WICG specification repository.

## Table of Contents

- [Minimal Setup Pattern](#minimal-setup-pattern)
- [Complex Rotated Text (2D Canvas)](#complex-rotated-text)
- [Interactive Form (Text Input)](#interactive-form)
- [Accessible Pie Chart](#accessible-pie-chart)
- [WebGL 3D Cube with HTML Texture](#webgl-3d-cube)
- [OffscreenCanvas Worker Pattern](#offscreencanvas-worker-pattern)
- [Common Patterns and Recipes](#common-patterns-and-recipes)

## Minimal Setup Pattern

Every HTML-in-Canvas implementation needs these three things:

```html
<!-- 1. Canvas with layoutsubtree and child elements -->
<canvas id="canvas" layoutsubtree>
  <div id="content">Hello from HTML-in-Canvas!</div>
</canvas>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');

  // 2. Paint event handler — draw elements and sync transforms
  canvas.onpaint = () => {
    ctx.reset();
    const transform = ctx.drawElementImage(content, 0, 0);
    content.style.transform = transform.toString();
  };

  // 3. ResizeObserver for DPI-correct sizing + requestPaint for initial draw
  const observer = new ResizeObserver(([entry]) => {
    canvas.width = entry.devicePixelContentBoxSize[0].inlineSize;
    canvas.height = entry.devicePixelContentBoxSize[0].blockSize;
  });
  observer.observe(canvas, { box: 'device-pixel-content-box' });

  canvas.requestPaint();
</script>
```

## Complex Rotated Text

Demonstrates: multi-line formatted text, emoji, RTL, vertical text, inline images, SVG — all rotated on canvas.

```html
<!doctype html>
<style>
  canvas { border: 1px solid blue; width: 638px; height: 318px; }
</style>

<canvas id="canvas" width="638" height="318" layoutsubtree="true">
  <div id="draw_element" style="width: 550px;">
    Hello from <a href="https://github.com/WICG/html-in-canvas">html-in-canvas</a>!
    <br>I'm multi-line, <b>formatted</b>,
    rotated text with emoji (&#128512;), RTL text
    <span dir=rtl>من فارسی صحبت میکنم</span>,
    vertical text,
    <p style="writing-mode: vertical-rl;">这是垂直文本</p>
    an inline image (<img width="150" src="wolf.jpg">), and
    <svg width="50" height="50">
      <circle cx="25" cy="25" r="20" fill="green" />
      <text x="25" y="30" font-size="15" text-anchor="middle" fill="#fff">SVG</text>
    </svg>!
  </div>
</canvas>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  canvas.onpaint = (event) => {
    ctx.reset();
    ctx.rotate((15 * Math.PI) / 180);
    ctx.translate(80 * devicePixelRatio, -20 * devicePixelRatio);
    let transform = ctx.drawElementImage(draw_element, 0, 0);
    draw_element.style.transform = transform.toString();
  };
  canvas.requestPaint();

  const observer = new ResizeObserver(([entry]) => {
    canvas.width = entry.devicePixelContentBoxSize[0].inlineSize;
    canvas.height = entry.devicePixelContentBoxSize[0].blockSize;
  });
  observer.observe(canvas, { box: 'device-pixel-content-box' });
</script>
```

## Interactive Form

Demonstrates: fully interactive form controls (text inputs, checkboxes, radio buttons, range sliders, buttons) rendered inside canvas while remaining functional.

```html
<!doctype html>
<style>
  canvas { border: 1px solid blue; width: 638px; height: 318px; }
  form p { margin: 6px; }
</style>

<canvas id="canvas" width="638" height="318" layoutsubtree="true">
  <div id="draw_element" style="width: 578px">
    <form id="demo-form" action="#" method="get">
      <fieldset>
        <legend>Spaceship Control Panel</legend>
        <p>
          <label for="shipName">Ship Name:</label>
          <input type="text" id="shipName" value="The 'Canvas' Voyager">
        </p>
        <p>
          <input type="checkbox" id="hyperdrive" checked>
          <label for="hyperdrive">Engage Hyperdrive</label>
        </p>
        <fieldset>
          <legend>Target System</legend>
          <p>
            <input type="radio" id="alpha" name="system" value="alpha" checked>
            <label for="alpha">Alpha Centauri</label>
          </p>
          <p>
            <input type="radio" id="beta" name="system" value="beta">
            <label for="beta">Betelgeuse</label>
          </p>
        </fieldset>
        <p>
          <label for="shieldLevel">Shield Strength:</label>
          <input type="range" id="shieldLevel" min="0" max="100" value="75">
        </p>
        <p style="text-align: right; margin: 0;">
          <button type="submit">Launch!</button>
        </p>
      </fieldset>
    </form>
  </div>
</canvas>

<script>
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  canvas.onpaint = (event) => {
    ctx.reset();
    let x = canvas.width / 25;
    let y = canvas.height / 25;
    let transform = ctx.drawElementImage(draw_element, x, y);
    draw_element.style.transform = transform.toString();
  };
  canvas.requestPaint();

  const observer = new ResizeObserver(([entry]) => {
    canvas.width = entry.devicePixelContentBoxSize[0].inlineSize;
    canvas.height = entry.devicePixelContentBoxSize[0].blockSize;
  });
  observer.observe(canvas, { box: 'device-pixel-content-box' });
</script>
```

## Accessible Pie Chart

Demonstrates: accessible canvas content with ARIA roles, focus management, `drawFocusIfNeeded()`, computed label positioning, and radial gradients.

```html
<!doctype html>
<style>
  .pie { width: 250px; height: 250px; }
  .pie .label { text-align: center; max-width: 40%; font-family: sans-serif; }
  .pie .label .val { display: block; font-size: xx-large; font-weight: bold; }
</style>

<canvas layoutsubtree class="pie" role="list" aria-label="Pie Chart">
  <div class="label" role="listitem" tabindex="0"
       data-val="0.45" data-color="tomato">
    <span class="val">45%</span>Apple
  </div>
  <div class="label" role="listitem" tabindex="0"
       data-val="0.35" data-color="cornflowerblue">
    <span class="val">35%</span>Blackberry / Bramble
  </div>
  <div class="label" role="listitem" tabindex="0"
       data-val="0.20" data-color="gold">
    <span class="val">20%</span>Durian
  </div>
</canvas>

<script>
  const canvas = document.querySelector('canvas');
  const ctx = canvas.getContext('2d');

  canvas.onpaint = () => {
    ctx.reset();
    const radius = 0.95 * Math.min(canvas.width, canvas.height) / 2;
    ctx.translate(canvas.width / 2, canvas.height / 2);

    let angle = 0;
    let focusedPath = null;
    for (const label of canvas.children) {
      const slice = Number(label.dataset.val) * Math.PI * 2;

      // Draw pie slice with gradient
      const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, radius);
      grad.addColorStop(0, `color-mix(${label.dataset.color}, white 40%)`);
      grad.addColorStop(1, label.dataset.color);
      ctx.fillStyle = grad;
      const path = new Path2D();
      path.moveTo(0, 0);
      path.arc(0, 0, radius, angle, angle + slice);
      path.closePath();
      ctx.fill(path);

      // Track focused element for drawFocusIfNeeded
      if (document.activeElement === label)
        focusedPath = path;

      // Position label at center of slice
      const mid = angle + slice / 2;
      const label_width = label.offsetWidth * devicePixelRatio;
      const label_height = label.offsetHeight * devicePixelRatio;
      const x = Math.cos(mid) * radius * 0.60 - label_width / 2;
      const y = Math.sin(mid) * radius * 0.60 - label_height / 2;
      const transform = ctx.drawElementImage(label, x, y);
      label.style.transform = transform;

      angle += slice;
    }

    // Draw focus ring for accessibility
    if (focusedPath)
      ctx.drawFocusIfNeeded(focusedPath, document.activeElement);
  };
  canvas.requestPaint();

  new ResizeObserver(([entry]) => {
    const box = entry.devicePixelContentBoxSize[0];
    canvas.width = box.inlineSize;
    canvas.height = box.blockSize;
  }).observe(canvas, { box: ['device-pixel-content-box'] });
</script>
```

## WebGL 3D Cube

Demonstrates: using `texElementImage2D()` to render HTML as a WebGL texture on a 3D rotating cube. Note: child element uses `inert` since interaction is in 3D space.

```html
<!doctype html>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gl-matrix/2.8.1/gl-matrix-min.js"
        crossorigin="anonymous" defer></script>
<style>
  canvas { border: 1px solid blue; width: 638px; height: 318px; }
  #draw_element { border: 1px solid blue; width: 400px; height: 400px; padding: 10px; }
</style>

<canvas id="gl-canvas" width="638" height="318" layoutsubtree="true">
  <div id="draw_element" inert>
    Hello world!<br>I'm multi-line, <b>formatted</b>,
    rotated text with emoji (&#128512;)
  </div>
</canvas>

<script>
  function loadTexture(gl) {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texElementImage2D(
      gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, draw_element
    );
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return texture;
  }

  onload = () => {
    const canvas = document.querySelector('#gl-canvas');
    canvas.onpaint = () => {
      const gl = canvas.getContext('webgl2');
      // ... standard WebGL setup (shaders, buffers, etc.)
      const texture = loadTexture(gl);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
      // ... render loop with requestAnimationFrame
    };
    canvas.requestPaint();

    const observer = new ResizeObserver(([entry]) => {
      canvas.width = entry.devicePixelContentBoxSize[0].inlineSize;
      canvas.height = entry.devicePixelContentBoxSize[0].blockSize;
    });
    observer.observe(canvas, { box: 'device-pixel-content-box' });
  };
</script>
```

## OffscreenCanvas Worker Pattern

Demonstrates: capturing element image, transferring to worker, drawing on OffscreenCanvas, and syncing transform back to main thread.

```html
<canvas id="canvas" style="width: 400px; height: 200px;" layoutsubtree>
  <form id="form_element">
    <label for="name">name:</label>
    <input id="name">
  </form>
</canvas>

<script>
  const workerCode = `
    let ctx;
    self.onmessage = (e) => {
      if (e.data.canvas) {
        ctx = e.data.canvas.getContext('2d');
      }
      if (e.data.width && e.data.height) {
        ctx.canvas.width = e.data.width;
        ctx.canvas.height = e.data.height;
      }
      if (e.data.elementImage) {
        ctx.reset();
        const transform = ctx.drawElementImage(e.data.elementImage, 100, 0);
        self.postMessage({ transform: transform });
      }
    };
  `;

  const worker = new Worker(URL.createObjectURL(new Blob([workerCode])));
  const offscreen = canvas.transferControlToOffscreen();
  worker.postMessage({ canvas: offscreen }, [offscreen]);

  canvas.onpaint = (event) => {
    const elementImage = canvas.captureElementImage(form_element);
    worker.postMessage({ elementImage }, [elementImage]);
  };

  worker.onmessage = ({ data }) => {
    form_element.style.transform = data.transform.toString();
  };

  const observer = new ResizeObserver(([entry]) => {
    worker.postMessage({
      width: entry.devicePixelContentBoxSize[0].inlineSize,
      height: entry.devicePixelContentBoxSize[0].blockSize
    });
    canvas.requestPaint();
  });
  observer.observe(canvas, { box: 'device-pixel-content-box' });
</script>
```

## Common Patterns and Recipes

### DPI-Correct Canvas Sizing

Always use `device-pixel-content-box` for sharp rendering on high-DPI displays:

```js
new ResizeObserver(([entry]) => {
  const box = entry.devicePixelContentBoxSize[0];
  canvas.width = box.inlineSize;
  canvas.height = box.blockSize;
}).observe(canvas, { box: 'device-pixel-content-box' });
```

### Centering an Element on Canvas

```js
canvas.onpaint = () => {
  ctx.reset();
  const ew = element.offsetWidth * devicePixelRatio;
  const eh = element.offsetHeight * devicePixelRatio;
  const x = (canvas.width - ew) / 2;
  const y = (canvas.height - eh) / 2;
  const transform = ctx.drawElementImage(element, x, y);
  element.style.transform = transform.toString();
};
```

### Drawing Multiple Elements

```js
canvas.onpaint = () => {
  ctx.reset();
  // Draw background
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Draw each child at different positions
  for (const [i, child] of [...canvas.children].entries()) {
    const x = i * 200 * devicePixelRatio;
    const transform = ctx.drawElementImage(child, x, 20);
    child.style.transform = transform.toString();
  }
};
```

### Applying Canvas Transforms Before Drawing

```js
canvas.onpaint = () => {
  ctx.reset();
  ctx.save();
  ctx.translate(canvas.width / 2, canvas.height / 2);
  ctx.rotate(angle);
  ctx.scale(2, 2);
  const transform = ctx.drawElementImage(element, -50, -50);
  element.style.transform = transform.toString();
  ctx.restore();
};
```

### Conditional Redraw with changedElements

```js
canvas.onpaint = (event) => {
  if (event.changedElements.includes(myElement)) {
    // Only redraw what changed
    ctx.clearRect(dirtyX, dirtyY, dirtyW, dirtyH);
    const transform = ctx.drawElementImage(myElement, dirtyX, dirtyY);
    myElement.style.transform = transform.toString();
  }
};
```

### Focus Management for Accessibility

```js
canvas.onpaint = () => {
  // ... draw content ...
  // Draw focus ring around active element
  if (canvas.contains(document.activeElement)) {
    const path = elementPaths.get(document.activeElement);
    if (path) ctx.drawFocusIfNeeded(path, document.activeElement);
  }
};
```
