# Intelligent Dithering — brand export pack

## Colours

| Name  | Hex       | Use |
|-------|-----------|-----|
| Teal  | `#1A9BAA` | Mark, "Dithering", accents |
| Ink   | `#0F1B24` | Dark backgrounds, "Intelligent" on light |
| Paper | `#F4F1EA` | Light backgrounds, "Intelligent" on dark |

Font: **Inter**, ExtraBold for the wordmark and Medium for the tagline. Every SVG has its text converted to outlines, so you don't need the font installed.

## What goes where

**YouTube**
- Profile picture: `youtube/avatar-800-dark.png`
- Banner: `youtube/banner-2560x1440-dark.png` (the content sits inside the 1546×423 area that shows on every device)
- Video watermark: `youtube/watermark-150.png` (white on transparent)

**Beehiiv**
- Publication logo: `beehiiv/publication-logo-1000-dark.png`
- Email header: `beehiiv/email-header-1200x300-light.png` (shown at 2× for retina)
- Social/OG image: `social/og-card-1200x630.png`

**Hugo site:** copy everything in `web/` into the site's `static/` folder, then add this to the head partial:

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:image" content="{{ "og-image.png" | absURL }}">
```

The header logo is `web/logo-header.svg`, or `logo-header-light-text.svg` for a dark header.

**General use:** see `logo/`.
- `mark-*`: the head on its own
- `lockup-stacked-*`: the head with the name on two lines
- `lockup-inline-*`: the head with the name on one line
- Each comes as an SVG plus a PNG.

## Rules
- Favicons at 48px and below use the solid silhouette, because the dithering turns to mush at that size.
- Use the dithered mark at 64px and above.
- Don't recolour the mark beyond the three colours above or white.
- Leave at least half the head's width as clear space around it.
- `export.py` (in `branding/`) regenerates the whole pack.
