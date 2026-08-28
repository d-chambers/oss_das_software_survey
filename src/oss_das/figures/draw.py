"""Primitives for the hand-composed SVG figures.

These figures are typographic infographics, not charts: the information is
carried by a number, a label, and their arrangement. A plotting library would
impose axes and a legend on material that has neither, so the drawing is done
directly and the vocabulary is kept small on purpose -- a column, a spine, an
arrow, a chip. Anything that cannot be said with those probably wants to be a
different figure.

Every colour and size is a named token so the eight figures stay one family.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from xml.sax.saxutils import escape

#: The palette, carried over from the conference figures it has to sit beside.
INK = "#2b2620"
MUTED = "#7a7266"
FAINT = "#a3825a"
RULE = "#cbc3b3"
CREAM = "#e4dccb"
PALE = "#f1ece1"
AMBER = "#c98500"
SLATE = "#4b4b50"
GRAY = "#b8b0a0"
PAPER = "#ffffff"

SERIF = "Georgia, 'Times New Roman', serif"

#: Type scale. Figures use these sizes and no others.
HERO = 104
BIG = 76
MID = 52
LABEL = 24
LABEL_SM = 20
SUB = 21
SUB_SM = 19
TINY = 15


#: Centred text with letter-spacing renders half a space left of true centre,
#: because the spacing is added after the final glyph too.
def _centre(x: float, spacing: float, anchor: str) -> float:
    return x + spacing / 2 if anchor == "middle" and spacing else x


@dataclass
class Canvas:
    """An SVG document being assembled, in user units."""

    width: int
    height: int
    title: str
    desc: str
    parts: list[str] = field(default_factory=list)

    def text(
        self,
        x: float,
        y: float,
        content: str,
        *,
        size: float = SUB,
        fill: str = INK,
        anchor: str = "middle",
        italic: bool = False,
        spacing: float = 0.0,
        upper: bool = False,
    ) -> None:
        if upper:
            content = content.upper()
        attrs = [
            f'x="{_centre(x, spacing, anchor):g}"',
            f'y="{y:g}"',
            f'font-size="{size:g}"',
            f'fill="{fill}"',
            f'text-anchor="{anchor}"',
        ]
        if italic:
            attrs.append('font-style="italic"')
        if spacing:
            attrs.append(f'letter-spacing="{spacing:g}"')
        self.parts.append(f"<text {' '.join(attrs)}>{escape(content)}</text>")

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        stroke: str = RULE,
        width: float = 3,
        dash: str | None = None,
    ) -> None:
        dashed = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<path d="M {x1:g},{y1:g} L {x2:g},{y2:g}" stroke="{stroke}"'
            f' stroke-width="{width:g}" fill="none"{dashed}/>'
        )

    def dot(self, x: float, y: float, r: float = 7, fill: str = INK) -> None:
        self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}"/>')

    def arrow(self, x1: float, x2: float, y: float, *, stroke: str = RULE) -> None:
        """A horizontal arrow with a solid head, pointing right."""
        head = 26
        self.line(x1, y, x2 - head, y, stroke=stroke, width=3)
        self.parts.append(
            f'<path d="M {x2 - head:g},{y - 11:g} L {x2:g},{y:g} '
            f'L {x2 - head:g},{y + 11:g} Z" fill="{stroke}"/>'
        )

    def down_arrow(
        self,
        x: float,
        y1: float,
        y2: float,
        *,
        stroke: str = RULE,
        dash: str | None = None,
    ) -> None:
        head = 22
        self.line(x, y1, x, y2 - head, stroke=stroke, width=3, dash=dash)
        self.parts.append(
            f'<path d="M {x - 10:g},{y2 - head:g} L {x:g},{y2:g} '
            f'L {x + 10:g},{y2 - head:g} Z" fill="{stroke}"/>'
        )

    def stat(
        self,
        x: float,
        y: float,
        number: str,
        label: str,
        sub: str = "",
        *,
        size: float = BIG,
        colour: str = INK,
        label_size: float = LABEL_SM,
        sub_size: float = SUB_SM,
        gap: float = 38,
        sub_gap: float = 32,
    ) -> float:
        """A number over a small-caps label over an italic gloss.

        Returns the y of the last line drawn, so callers can stack blocks
        without recomputing offsets by hand.
        """
        self.text(x, y, number, size=size, fill=colour)
        y += gap
        self.text(x, y, label, size=label_size, fill=INK, spacing=2.4, upper=True)
        if sub:
            y += sub_gap
            self.text(x, y, sub, size=sub_size, fill=MUTED, italic=True)
        return y

    def spine(self, x1: float, x2: float, y: float, dots: list[float]) -> None:
        self.line(x1, y, x2, y, stroke=RULE, width=3)
        for x in dots:
            self.dot(x, y)

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        fill: str = CREAM,
        rx: float = 0,
    ) -> None:
        radius = f' rx="{rx:g}"' if rx else ""
        self.parts.append(
            f'<rect x="{x:g}" y="{y:g}" width="{max(w, 0):g}" height="{h:g}"'
            f'{radius} fill="{fill}"/>'
        )

    def bar_stack(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        segments: list[tuple[str, float, str]],
        *,
        min_visible: float = 3.0,
    ) -> list[tuple[str, float, float]]:
        """Draw one stacked horizontal bar; return each segment's span.

        A segment with a tiny share is widened to ``min_visible`` so that a
        real category never renders as nothing -- a zero-width bar reads as
        absence, and absence is a different claim from "small".
        """
        total = sum(value for _, value, _ in segments) or 1.0
        cursor = x
        spans = []
        for label, value, colour in segments:
            span = max(width * value / total, min_visible if value else 0.0)
            self.rect(cursor, y, span, height, fill=colour)
            spans.append((label, cursor, span))
            cursor += span
        return spans

    def to_svg(self) -> str:
        body = "\n  ".join(self.parts)
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n'
            f'     width="{self.width}" height="{self.height}"'
            f' viewBox="0 0 {self.width} {self.height}">\n'
            f"  <title>{escape(self.title)}</title>\n"
            f"  <desc>{escape(self.desc)}</desc>\n"
            f'  <rect x="0" y="0" width="{self.width}" height="{self.height}"'
            f' fill="{PAPER}"/>\n'
            f'  <g font-family="{SERIF}" text-anchor="middle">\n'
            f"  {body}\n"
            "  </g>\n"
            "</svg>\n"
        )
