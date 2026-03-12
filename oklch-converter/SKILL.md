---
name: oklch-converter
description: >
  Convert CSS colors between HSL and OKLCH color spaces with mathematical accuracy.
  Use when: (1) migrating a CSS codebase from HSL to OKLCH or vice versa, (2) the user
  asks to "convert colors", "hsl to oklch", "oklch to hsl", (3) adding new color values
  to an OKLCH-based theme, (4) verifying color equivalence across color spaces.
---

# OKLCH Color Converter

## Overview

OKLCH (Oklab Lightness-Chroma-Hue) is a perceptually uniform color space. Unlike HSL, equal numeric steps produce equal perceived brightness/saturation changes, making it ideal for design systems.

## Format

```
HSL:   H S% L%        e.g. 192 100% 50%
OKLCH: L% C H         e.g. 89.03% 0.1739 171.27
```

- **L** (Lightness): 0% to 100%
- **C** (Chroma): 0 to ~0.4 (most colors fall under 0.3)
- **H** (Hue): 0 to 360 degrees
- Achromatic colors (saturation = 0): use `none` for hue, e.g. `59.82% 0 none`

## Conversion Script

Run the Node.js script at `script/oklch-convert.js` to convert HSL values to OKLCH. Edit the `colors` array in the script with your `[name, H, S, L]` tuples, then run:

```bash
node ~/.claude/skills/oklch-converter/script/oklch-convert.js
```

## How to Apply

When converting a CSS file from HSL to OKLCH:

1. **Run the script** with all HSL values from the file to get OKLCH equivalents
2. **Update CSS variable values** from `H S% L%` to `L% C H` format
3. **Update wrapper functions** from `hsl(var(--name))` to `oklch(var(--name))`
4. **Update inline colors** in gradients, shadows, and keyframes from `hsl(...)` to `oklch(...)`
5. **Search the entire codebase** for `hsl(` in `.ts`, `.tsx`, `.js`, `.jsx` files — JS/TS code that reads CSS variables and wraps them in template literals (e.g. `` `hsl(${value})` ``) must also be updated
6. **Verify the build** passes after all changes

## Quick Reference: Common Conversions

| HSL | OKLCH | Description |
|-----|-------|-------------|
| `0 0% 0%` | `0% 0 none` | Black |
| `0 0% 100%` | `100% 0 none` | White |
| `0 0% 50%` | `59.82% 0 none` | Mid gray |
| `0 100% 50%` | `62.80% 0.2577 29.23` | Pure red |
| `120 100% 50%` | `86.64% 0.2948 142.50` | Pure green |
| `240 100% 50%` | `45.20% 0.3132 264.05` | Pure blue |
| `180 100% 50%` | `90.54% 0.1546 194.77` | Pure cyan |
| `60 100% 50%` | `96.80% 0.2115 109.77` | Pure yellow |
