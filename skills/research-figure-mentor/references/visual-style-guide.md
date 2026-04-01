# Visual Style Guide

## General Style

- Favor clean, paper-ready layouts over decorative complexity.
- Make visual hierarchy obvious through placement, spacing, border weight, and restrained color use.
- Use whitespace intentionally. Dense is acceptable only if the reading path remains obvious.

## Color Discipline

- Keep the primary palette to about 4-6 semantic colors per figure.
- Reuse the same color for the same functional family within one figure set.
- Use neutral grays for auxiliary edges, notes, or background guides.
- Reserve saturated warm colors for highlights, anomalies, or warnings.

Use [../assets/palette-presets.json](../assets/palette-presets.json) as a starting point.

## Text

- Prefer short labels inside boxes.
- Use consistent title case or sentence case inside one figure.
- Keep font size large enough for paper and slide reuse.
- Avoid text blocks that are so long that they become paragraphs inside nodes.

## Alignment

- Align peer boxes on the same baseline when they serve the same layer.
- Maintain consistent spacing between repeated blocks.
- Avoid “almost aligned” placement; it looks accidental and creates drift.

## Arrows

- Use the same arrow style for the same semantic relation.
- Prefer straight or gently bent routes.
- Minimize crossings.
- If crossings are unavoidable, separate them clearly and avoid touching box text.

## Figure Titles

- For paper-facing figures, prefer informative titles that reveal the main point.
- For neutral system or model diagrams, prefer direct descriptive titles.
