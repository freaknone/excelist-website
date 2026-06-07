# Geometry Report

## Overall dimensions
- Source reconstruction footprint: `593 x 560` units.
- Final SVG viewBox: `0 0 1024 1024`.
- Placement strategy: the rebuilt logo is authored in source-space units and scaled by `1.7268128` with a vertical offset of `28.0202` to preserve the source aspect ratio inside the square artboard.

## ViewBox
- Root SVG: `width="1024" height="1024" viewBox="0 0 1024 1024"`.
- Main content group: `transform="translate(0 28.0202) scale(1.7268128)"`.

## Gradient definitions
- `bgGradient`: dark background tile, `x1="0" y1="0" x2="593" y2="560"`.
- `kBodyGradient`: primary blue body gradient, `x1="275.5" y1="375" x2="420" y2="153.5"`.
- `pixelGradient`: upper cluster gradient, `x1="115.8" y1="132" x2="291.3" y2="247.9"`.
- `barGradient`: chart bar gradient, `x1="148.2" y1="342.9" x2="306.4" y2="165.6"`.
- `arrowGradient`: main arrow gradient, `x1="59.1" y1="430.9" x2="500.3" y2="112.3"`.
- `curveGradient`: inner growth sweep gradient, `x1="97.3" y1="375.3" x2="423.3" y2="169.7"`.
- `wordGradient`: wordmark silver gradient, `x1="35.5" y1="441" x2="554" y2="441"`.
- `tagGradient`: tagline blue gradient, `x1="62.5" y1="517" x2="522" y2="517"`.

## Coordinates of major shapes
- `k_body`
  - stem + lower leg path: `M275.5 153.5H307.5V229.5L418 375H353L307.5 317.5V375H275.5Z`
- `pixel_cluster`
  - overall cluster extent: approximately `x=115.8..291.3`, `y=132..247.9`
  - built from `11` cells: `6` rectangles and `5` triangular corner cells
- `chart_bars`
  - bar 1: `x=148.2 y=289 w=31.3 h=53.9`
  - bar 2: `x=190.5 y=247.9 w=31.3 h=95`
  - bar 3: `x=232.8 y=206.7 w=31.3 h=136.1`
  - bar 4: `x=275.1 y=165.6 w=31.3 h=177.2`
- `growth_curve`
  - stroke path: `M97.3 375.3C180.1 366.6 243.8 339.9 300 294.2C341.7 260 375.3 220.6 423.3 169.7`
  - stroke width: `13.9`
- `arrow`
  - fill path begins at `M59.1 369.5` and terminates at `... 59.1 369.5Z`
  - overall arrow extent: approximately `x=49.2..514.8`, `y=110.6..433.2`
- `wordmark`
  - contour-derived outlined path spanning approximately `x=35.5..554`, `y=406.5..475.5`
- `tagline`
  - contour-derived outlined path spanning approximately `x=62.5..522`, `y=505.5..528.5`

## Grouping structure
- `logo_lockup`
  - background rect
  - `k_body`
  - `pixel_cluster`
  - `chart_bars`
  - `growth_curve`
  - `arrow`
  - `wordmark`
  - `tagline`

## Optimization notes
- No raster content, `<image>` tags, or base64 payloads are used.
- Reusable gradients are centralized in `defs`.
- Typography is stored as contour paths rather than text elements to avoid font dependency drift.
- The symbol is kept to a low path count by using rectangles for bars, simple triangular cells for the cluster, and single-path definitions for the body and arrow.
- The wordmark and tagline were contour-derived from `master_logo_clean.png` to preserve spacing and proportions more closely than a substituted font would.
