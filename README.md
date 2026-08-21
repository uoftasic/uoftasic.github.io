# uoftasic.com

The UofT ASIC Team website. Jekyll, deployed by GitHub Pages' built-in builder
from `master` — there is no CI workflow and no build step to babysit. Push to
`master` and Pages rebuilds.

Because Pages uses its **legacy** builder, the site is pinned to Jekyll 3.x and
the plugins Pages whitelists. The `github-pages` gem in the `Gemfile` reproduces
that exact set locally, so a local build matches production.

## Adding content

Everything is markdown with front matter. You should never need to touch a
layout or the stylesheet.

### A new project

Copy `_projects/TEMPLATE.md` to `_projects/<slug>.md`, set `published: true`,
and fill in the front matter. It appears on `/projects/` and, if
`featured: true`, its render becomes the home page hero.

`pdk:` is its own field rather than a row in `specs:`, because the process and
the design name are what identify a layout to an IC engineer — they are the two
facts on the home page hero, and the PDK leads both the spec rail and the
project card.

The `specs:` map is free-form — whatever keys you write become the specification
rail on the project page, in the order you write them. A digital project lists
cell counts; an analog one can list gain and bandwidth. The first five values
also show as chips on the projects index.

`status:` is one of `concept`, `in-design`, `verification`, `taped-out`,
`silicon-back`. Anything else renders as a neutral chip showing the raw value,
so a typo is visible rather than silent.

### A new post

Copy `_posts/TEMPLATE.md.example` to `_posts/YYYY-MM-DD-slug.md`. The date in
the filename sets both the URL (`/blog/<slug>/`) and the publication date.

Set `project: <slug>` to cross-link a post and a project — the link appears on
both pages, in each direction.

### Equations

Add `math: true` to a page's front matter and write LaTeX directly:
`$V_{th} \approx 0.45\,\text{V}$` inline, or `$$ ... $$` on its own lines for a
display equation. KaTeX renders it in the browser and loads **only** on pages
that opt in.

### Layout renders

Tiny Tapeout publishes a permanent render of every shuttle project at
`github.com/TinyTapeout/tinytapeout-project-renders`. The images in
`assets/projects/` are those renders re-coloured from KLayout's default neon
layer palette into the U of T palette — layer colours are a display convention,
so the geometry is untouched. `script/reink-render.py` does the re-colouring.

## Running it locally

Either works. Use Docker if you would rather not install Ruby.

```bash
# Docker — no local Ruby needed. Gems install into vendor/ on first run.
npm run build:docker
npm run serve:docker      # http://127.0.0.1:4000

# Native — needs Ruby and bundler
bundle install
npm run build
npm run serve             # http://127.0.0.1:4000
```

`script/jekyll` is the Docker wrapper behind the `:docker` scripts; it runs any
Jekyll command (`script/jekyll build --verbose`) as your own user, so nothing in
the working tree ends up owned by root.

## Tests

Structural checks rather than pixel comparison: HTTP status, console errors,
horizontal overflow at desktop and phone widths, the spec rail collapsing to a
two-up grid on narrow screens, the JavaScript-free nav being keyboard operable,
and KaTeX loading only where requested.

```bash
npm install
npx playwright install chromium
npm run build:docker      # the suite serves _site, so build first
npm run test:visual
```

Stop any dev server on port 4000 first. Playwright reuses an existing server, so
a running `serve` container would be tested instead of the build you just made —
and `jekyll serve` overrides `site.url` with the local address.

## Design notes

- **Palette** is the University of Toronto's own. U of T Blue (`#1E3765`,
  Pantone 655) is the sole primary; the secondary colours exist, per the
  university's guidelines, "to add vibrancy and energy" and are used only for
  status, table headers, rules and eyebrows. Single light theme by design.
- **Type** is Archivo (display and UI, using its width axis), Newsreader
  (article prose), IBM Plex Mono (every number, tabular).
- **The mark** in `assets/brand/` is a maple leaf snapped to a manufacturing
  grid — the constraint every layout is drawn under. Keep the central lobe
  compact; elongating it stops the shape reading as a leaf. `mark.svg` uses
  `currentColor` and is inlined by `_includes/mark.html`.
- **No JavaScript ships with the site** apart from KaTeX on pages that ask for
  it. The mobile navigation is a CSS-only checkbox toggle.
