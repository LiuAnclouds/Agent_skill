# Validation Checklist

Run automated validation first, then do a manual pass.

## Automated Checks

- renderer-first figures: run the JSON validators so bounding boxes stay within the canvas, arrows reference valid nodes, and labels are not obviously too long for their containers
- native Python figures: run a render dry-run at target export size and confirm the script completes without clipping, missing assets, or broken math text
- legend entries or semantic color families stay consistent
- color count stays disciplined
- render reports are written alongside the first-pass export when the renderer is used

## Manual Checks

- the figure tells the right story for the intended audience
- the title matches the actual content
- the dominant signal is visually dominant
- color semantics are consistent
- labels are readable at realistic export size
- branch order and fusion order are faithful
- no misleading simplification was introduced
- inset graphs, tensor depth faces, and panel titles do not collide in native Python layouts
- cross-panel arrows land between panels instead of through labels
- graph insets are semantic and stage-specific, not decorative placeholders
- when a subgraph evolves across panels, node roles, anchor positions, and color meaning remain stable enough to follow
- callouts from tensor/embedding blocks point to meaningful graph elements rather than empty space
- the final readout view explains why the target is anomalous instead of ending with an unrelated generic network icon

## Drift Checks

Check for drift both before and after refinement:

- alignment drift
- arrow endpoint drift
- label offset drift
- legend color drift
- semantic drift from the real source object

## Required Validation Flow

1. first automated pass
2. first manual pass
3. reference-driven refinement when required
4. second automated pass
5. second manual pass
