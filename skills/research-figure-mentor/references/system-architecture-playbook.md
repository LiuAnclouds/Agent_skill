# System Architecture Playbook

## Goal

Explain how a project works as a system, not just what files exist.

## Extraction Checklist

Extract these items before selecting a diagram form:

- system boundary
- internal modules
- external services or data sources
- primary user or caller
- control flow
- data flow
- optional or failure paths
- persistent stores or caches

## Diagram Type Selection

- Use module architecture when the main question is “what subsystems exist and how are they grouped?”
- Use a flowchart when the main question is “what happens step by step?”
- Use a sequence or interaction diagram when the main question is “who calls whom and in what order?”
- Use a dataflow diagram when the main question is “what data is produced, transformed, stored, and consumed?”

## Layout Rules

- Put the main path in the strongest visual channel:
  - central placement
  - darker arrows
  - stronger box borders
- Place peers on aligned rows or columns.
- Reserve dashed arrows or lighter edges for optional, diagnostic, or background paths.
- Use short module names; move long explanations into callouts, captions, or footnotes.

## Naming Rules

- Use one naming scheme per figure.
- If the audience is engineering-heavy, prefer real module names.
- If the audience is mixed, use descriptive labels and mention code identifiers only where needed.
- Do not rename the same module multiple ways across the figure.

## Common Failure Modes

- too many boxes on one plane with no hierarchy
- arrows crossing through boxes
- mixing runtime flow and static ownership without visual distinction
- using color only decoratively
- treating “system architecture” as a directory tree
