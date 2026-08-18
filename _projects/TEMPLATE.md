---
# Copy this file to _projects/<slug>.md, set published: true, and delete this line.
published: false

title: "Project name"
slug: project-name            # must match the filename; used to cross-link posts
summary: "One sentence on what it does. Shown on the projects index and the home page."
status: in-design             # concept | in-design | verification | taped-out | silicon-back
date: 2026-01-01              # sorts the projects index, newest first
featured: false               # true puts this project's render behind the home page hero

# Optional. Drop a layout render in assets/projects/ and point at it here.
# render: /assets/projects/<slug>-die.png    # card + spec rail
# hero:   /assets/projects/<slug>-hero.png   # full-bleed home hero (featured only)
# caption: "GDS layout"       # shown in the home hero caption strip
# image: /assets/projects/<slug>-og.png   # social preview
# repo: https://github.com/uoftasic/<repo>
# authors: "Name, Name"

# Free-form. Whatever keys you write become the specification rail, in order,
# so an analog project can list gain and bandwidth instead of cell counts.
# The first five values also appear as chips on the projects index.
specs:
  Process: SKY130
  Shuttle: TTSKY25b
  Die area: 1 × 1 tile
  Clock: 50 MHz
---

Write the project here in normal markdown. Headings become sections.

## Tables render as datasheet tables

Use markdown's own column alignment for numbers — `|---:|` right-aligns.

| Metric | Value |
|---|---:|
| Standard cells | 1,234 |

## Equations

Add `math: true` to the front matter above, then write LaTeX: `$V_{th}$` inline,
or `$$ ... $$` on its own lines for a display equation.
