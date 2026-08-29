# Repository instructions

- Add no AI/tool attribution or AI `Co-Authored-By` trailers to commits, PRs, or comments; write as the user.
- Do not hard-wrap Markdown prose; preserve normal blank-line separation.
- Use `AGENTS.md`, not `CLAUDE.md`, for repository-level instructions.
- Follow an applicable PR template when authoring a pull request.
- Do not use coverage pragmas without explicit permission. Prefer assertions for worthwhile defensive checks that should be unreachable.

## Pipeline stages

Scripts are prefixed by stage: `a` curate, `b` measure, `c` present, `v` figures. Each script's docstring says what it reads and writes.

- `s` is a reference ecosystem measured for comparison, under `data/comparison/<name>/`. It is deliberately not `data/raw/candidates/`: the funnel counts every file there, so a second ecosystem stored alongside the first would silently change this one's arithmetic.
- Comparing two ecosystems means measuring both the same way. The catalogue's dependency record merges declared manifests with an import scan, and the import half needs a clone; a reference ecosystem read over an API can only offer manifests. That is why `dependency_record` keeps a separate `declared` field, and why both sides of a comparison read it rather than the merged lists.

## Figures

Figures are for a conference slide read from the back of a room, not for a page.

- One `v<NNN>_<name>.py` script per figure in `scripts/`, writing an output named after the script, so a figure on a slide always says what produced it. `v000_build_all.py` runs every one.
- A script writes SVG and PNG by default; PDF only with `--pdf`. The PNG is what goes into PowerPoint. Export is cropped to the ink (`--export-area-drawing`) with a small margin, so a plate's leftover slack never reaches the slide.
- Canvases are transparent. Never paint a background unless asked: the deck's own background must show through.
- Every measurement lives in `figures/data.py` and every arrangement in `figures/plates.py`. A plate is handed a frozen measurement and never computes a number, so a figure and its dataset cannot drift.
- Count from the measured layers under `data/measured/`, never from a curated record's proposed field. Curation says what to go and look for; measurement says what was found, and the two disagree in both directions.
- Assert the arithmetic a figure implies. A funnel whose stages do not sum to its total, or a pair of numbers a reader is invited to add, should fail the build rather than print a lie.

### Building one at the keyboard

A figure built in conversation is not a change to be shipped. Do what was asked and review the figure yourself; the person asking is the reviewer and is already in the room. Skip the Definition of Done for it: no counterpart CLI review, no `.scratch/` write-up, no waiting on either.

- Measure both axes before proposing anything. A variable that turns out to be 75 of 77 one way is a sentence, not an encoding, and that is worth knowing before a plate exists.
- Bring the numbers and let the asker pick the framing. Columns, split, and denominator are theirs to choose.
- Render it and look at the PNG. A plate that reads fine as code prints duplicated numbers, letterboxes, or sets its labels too small for the back of a room, and none of that is visible until it is an image.
- Still run the tests and lint, and still assert the arithmetic. Those are cheap, and they are what stops a figure printing a lie.

### What goes on a slide

- No prose. Delete explanatory sentences, glosses under statistics, and axis notes; the presenter says those out loud. Keep the detail in the SVG `<desc>`, which is what it is for.
- Labels are words, not phrases: "Docs", not "Documentation"; "Authors > 1", not "Two or more authors". Shorten until shortening would make it ambiguous.
- Set labels around 30pt on the standard 1680-unit canvas. If a figure has a title at all, it is short; most figures have none, because the slide carries the title.
- Prefer one band to three. If a figure has stacked sections, ask whether the slide needs more than the strongest one.
- Aim wider than 16:9. A figure taller than it is wide will letterbox to a third of the slide.
- SVG collapses runs of whitespace, so a legend cannot be spaced apart by padding a string. Draw swatches and position each entry.

## The deck

`cd deck && quarto render` builds both outputs: `talk.html` to present from, `talk.pdf` as the backup. That is the whole build: `_quarto.yml` names `prepare.py` as a pre-render step, so quarto runs it. `quarto render --profile notes --output talk-notes.pdf` writes the speaker notes alone.

- **A number on a slide is a reference, never a literal.** Slides cite `{{< meta n.<path> >}}` into `figures/figures.json`; a key the sidecar does not define stops the render. The deck this replaced hard-coded its numbers and said 78 projects on one slide and 77 on the next.
- **Name the numbers a slide quotes.** `sidecar()` exports `hub`/`hub_dependents` rather than leaving them at `providers.0.2`: a positional path is not a citation anyone can read, and quarto cannot resolve one.
- Figures are cited by path, and `prepare.py` checks each against the checksum `v000_build_all.py` recorded. Modification times cannot do this -- git rewrites them all on checkout -- so it compares content.
- Hand-drawn SVGs are converted to PDF by the same step; beamer cannot place an SVG.
- `prepare.py` uses the standard library alone. Quarto invokes a pre-render script with the system interpreter, which cannot see this project's environment.
- `incremental: true` gives each bullet its own page with the frame title static. That is what animation means in a PDF.
- **Layout rules go in `ineris.css`, not the theme's scss.** A `scss:rules` block compiles silently to nothing when sass fails; plain CSS is inlined verbatim and cannot be dropped without noticing. Only variables belong in `ineris.scss`.
- **Absolute positioning is reveal-only.** A slide that places logos by coordinate must pair `when-format="revealjs"` with a `when-format="beamer"` fallback, or the PDF gets an empty slide. Use spans, not nested fenced divs: nesting defeats the filter and the hidden half leaks into the other format.
- Built outputs, `_numbers.yml` and `_svg/` are gitignored. The source is `slides.qmd`, `_theme.tex` and `assets/`.

## Definition of done

For substantive code, configuration, or documentation changes. Figure work done in conversation is exempt — see [Building one at the keyboard](#building-one-at-the-keyboard).

1. Run applicable tests and lint; all must pass.
2. Self-review for simpler approaches and duplicated methods or utilities.
3. Request a CLI review from Claude and save it temporarily under `.scratch/`; do not commit it.
4. Address actionable findings and rerun checks.
5. Report review status, exact checks and results, and anything not run.

