# HTML-in-Canvas Security and Privacy Model

## Core Security Principle

Since `drawElementImage()` makes rendered pixels accessible to scripts (via `getImageData()`, `toBlob()`, etc.), the API must prevent leaking sensitive information through the rendering pipeline.

## Sensitive Information EXCLUDED from Rendering

These are never painted into the canvas to prevent information leakage:

| Category | What's Excluded | Why |
|---|---|---|
| Cross-origin content | iframes, cross-origin images, URL references in CSS/SVG | Prevents reading pixels from other origins |
| System colors/themes | OS theme colors, system preference data | Prevents fingerprinting OS configuration |
| Spelling/grammar markers | Red/green underlines from spellcheck | Prevents revealing dictionary/language info |
| Visited link state | `:visited` link styling differences | Prevents history sniffing |
| Autofill previews | Pending form autofill data display | Prevents leaking saved credentials/data |

## Non-Sensitive Information ALLOWED in Rendering

These are permitted because they're necessary for interactivity or already accessible:

| Category | What's Allowed | Why |
|---|---|---|
| Search highlights | `find-in-page` and `text-fragment` markers | Already visible to user |
| Scrollbar appearance | Native scrollbar rendering | Necessary for interactive scrollable content |
| Form control rendering | Native input/button/checkbox appearance | Necessary for interactive forms |
| Caret blink rate | Text cursor blink timing | Minimal privacy impact, needed for text input |
| Forced-colors info | High contrast mode adaptations | Needed for accessibility compliance |

## Implementation Security Constraints

### Same-Origin Requirement
- Elements must be direct children of the canvas element
- No cross-origin content can be rendered into the canvas
- Cross-origin images within child elements are excluded from rendering

### Tainted Canvas Prevention
- Unlike `drawImage()` with cross-origin images, `drawElementImage()` proactively excludes cross-origin content rather than tainting the canvas
- The canvas remains usable for `toBlob()`, `toDataURL()`, and `getImageData()` after drawing

### No New Script Execution
- The API does not introduce new script execution or loading mechanisms
- No new attack surface for XSS or code injection

### No Persistent State
- No data persists across browsing sessions
- No new fingerprinting surface beyond what's already available
- Behavior is identical in private/incognito browsing modes

### No Platform Data Exposure
- Form autofill rendering is blocked
- OS-specific UI chrome is not leaked
- Device sensor data is not accessible

## Security Implications for Developers

### When using `inert` attribute
Mark WebGL/WebGPU child elements as `inert` when interaction should not occur in DOM space (e.g., 3D scene textures). This prevents unexpected form submission or link activation on elements that appear as 3D textures.

### ARIA and accessibility
Canvas fallback content with `layoutsubtree` maintains DOM correspondence for screen readers. Use proper ARIA roles (`role="list"`, `role="listitem"`, `tabindex`, `aria-label`) on canvas children for accessible canvas applications.

### Focus management
Use `drawFocusIfNeeded()` with `Path2D` to draw visible focus indicators on canvas for keyboard navigation accessibility.
