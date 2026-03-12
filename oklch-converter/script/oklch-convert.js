// Usage: node oklch-convert.js
// Edit the `colors` array below with [name, H, S, L] tuples

function hslToRgb(h, s, l) {
  s /= 100; l /= 100;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => {
    const k = (n + h / 30) % 12;
    return l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
  };
  return [f(0), f(4), f(8)];
}

function linearize(c) {
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function rgbToOklab(r, g, b) {
  r = linearize(r); g = linearize(g); b = linearize(b);
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [
    0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
    1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
    0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
  ];
}

function oklabToOklch(L, a, b) {
  const C = Math.sqrt(a * a + b * b);
  let h = Math.atan2(b, a) * 180 / Math.PI;
  if (h < 0) h += 360;
  return [L, C, h];
}

function convert(h, s, l) {
  const [r, g, b] = hslToRgb(h, s, l);
  const [L, a, bv] = rgbToOklab(r, g, b);
  const [oL, oC, oH] = oklabToOklch(L, a, bv);
  if (s === 0 || oC < 0.001) {
    return `${(oL * 100).toFixed(2)}% 0 none`;
  }
  return `${(oL * 100).toFixed(2)}% ${oC.toFixed(4)} ${oH.toFixed(2)}`;
}

// ---- Edit your colors here ----
const colors = [
  // [name, H, S, L]
  ["primary", 180, 80, 70],
  ["background", 0, 0, 5],
  ["accent", 192, 80, 40],
];

for (const [name, h, s, l] of colors) {
  console.log(`${name}: ${convert(h, s, l)}  (was hsl ${h} ${s}% ${l}%)`);
}
