# Verified style specification

## Evidence and scope

This specification separates verified implementation details from visual inference.

Verified from Anthropic's Newsroom HTML, CMS records, SVG assets, and CSS on 2026-07-18:

- The user-provided house image matches Anthropic's `Hand House` SVG asset. Its CMS record assigns the separate hero background `cactus`.
- The user-provided globe image matches Anthropic's `Object Globe` SVG asset. Its CMS record assigns the separate hero background `heather`.
- Both official SVGs use a transparent outer canvas, an internal ivory shape `#FAF9F5`, and black drawing `#141413`.
- The Newsroom sections use `data-theme="ivory"`; Anthropic CSS defines the primary ivory background as `#FAF9F5`.
- Anthropic's CSS exposes the accent palette below. The colored hero background is a separate presentation layer around the transparent SVG.

Official sources:

- Newsroom: https://www.anthropic.com/news
- Hand House asset: https://cdn.sanity.io/images/4zrzovbb/website/cd9cf56a7f049285b7c1c8786c0a600cf3d7f317-1000x1000.svg
- Object Globe asset: https://cdn.sanity.io/images/4zrzovbb/website/ffc0d7957a232518519f13c0d64896921ea215e2-1000x1000.svg

The generation guidance below generalizes that verified two-layer system to new topics. Metaphor selection and color-to-topic mapping are design heuristics, not official Anthropic rules.

## Palette

Use `#141413` for dominant linework and `#FAF9F5` for the internal carrier shape.

Choose one full-frame background:

| Token | Hex | Useful mood heuristic |
|---|---:|---|
| cactus | `#BCD1CA` | thoughtful, trustworthy, systems, institutions |
| heather | `#CBCADB` | global, technical, reflective, research |
| oat | `#E3DACC` | human, calm, operational, partnership |
| clay | `#D97757` | launch, urgency, energy, strong editorial emphasis |
| olive | `#788C5D` | growth, resilience, environment |
| sky | `#6A9BCC` | openness, infrastructure, communication |
| fig | `#C46686` | creativity, culture, identity |
| coral | `#EBCECE` | care, community, accessibility |

Use at most one accent family. Do not introduce a rainbow palette.

## Form grammar

- Draw with thick near-black strokes of inconsistent width and rounded ends.
- Prefer continuous, gestural contours with small wobbles and imperfect joins.
- Combine outline marks, solid black dots, and an irregular flat ivory silhouette.
- Simplify hands, heads, globes, houses, charts, plants, tools, and networks into symbolic marks.
- Use visual overlap to imply a relationship: a hand supports, frames, points to, holds, or transforms the core object.
- Keep at least 10% breathing room around the focal cluster.
- Avoid realistic perspective, anatomy, lighting, shading, gradients, and cast shadows.

## Background construction

Build exactly three visual layers:

1. Full-frame opaque accent field covering all corners.
2. One large irregular ivory carrier shape occupying roughly 55–80% of the canvas.
3. Near-black gestural linework and solid marks, with occasional controlled spill outside the carrier.

For a square card, keep the focal cluster centered or slightly off-center and sized to roughly 65–80% of the canvas. For a wide hero, move the cluster to one side only when the user needs copy space.

## Reference roles

- `assets/reference-hand-house.png`: study the irregular house carrier, solid node dots, and hand gesture.
- `assets/reference-object-globe.png`: study the irregular circular carrier, loose geographic contours, and large-scale simplicity.
- `assets/reference-hands-light.png`: study the continuous hand lines, paired-object rhythm, and asymmetrical vertical composition.

Do not copy the exact objects or layout unless the user's subject calls for them. Transfer stroke behavior, layering, density, and palette logic.

## Failure modes

- Transparent or checkerboard outer background: regenerate with an explicit opaque full-bleed field.
- White background: specify the exact accent hex and require colored corners.
- Generic stock vector: request naive ink gestures, rounded uneven strokes, deliberate asymmetry, and no perfect geometry.
- Too decorative: reduce to one metaphor and remove secondary objects.
- Too monochrome: retain black and ivory, then add exactly one accent background.
- Photographic texture or shadows: restate flat two-dimensional color with no lighting model.
