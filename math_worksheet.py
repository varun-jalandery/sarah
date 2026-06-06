#!/usr/bin/env python3
"""
Math Worksheet PDF Generator
Generates printable A4 pages with single-digit addition and subtraction problems.
Each problem includes a wide rectangle for kids to draw tally marks.
"""

import random
import argparse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = A4          # 595.28 x 841.89 pts
MARGIN = 45
COLS = 2
ROWS = 5
PROBLEMS_PER_PAGE = COLS * ROWS

CELL_W = (PAGE_W - 2 * MARGIN) / COLS
CELL_H = (PAGE_H - 2 * MARGIN - 60) / ROWS  # 60pt reserved for header

PROBLEM_FONT_SIZE = 36
RECT_HEIGHT = 38
RECT_CORNER_RADIUS = 4


def make_problems(count: int, op_mix: str) -> list[tuple[str, int, int]]:
    """Return a list of (operator, a, b) tuples of single-digit problems."""
    ops = []
    if op_mix == "add":
        ops = ["+"]
    elif op_mix == "sub":
        ops = ["-"]
    else:
        ops = ["+", "-"]

    problems = []
    while len(problems) < count:
        op = random.choice(ops)
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        if op == "-":
            # keep result >= 0 and avoid trivial x - x = 0
            if a < b:
                a, b = b, a
            if a == b:
                continue
        problems.append((op, a, b))
    return problems


def draw_page(c: canvas.Canvas, problems: list, page_num: int,
              title: str, show_page_num: bool) -> None:
    """Draw one A4 page of problems onto canvas c."""
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_W / 2, PAGE_H - MARGIN + 10, title)

    for idx, (op, a, b) in enumerate(problems):
        col = idx % COLS
        row = idx // COLS

        # Top-left corner of this cell
        cell_x = MARGIN + col * CELL_W
        cell_y = PAGE_H - MARGIN - 50 - (row + 1) * CELL_H  # bottom of cell

        # --- Problem text ---
        problem_text = f"{a}  {op}  {b}  ="
        c.setFont("Helvetica-Bold", PROBLEM_FONT_SIZE)
        text_y = cell_y + CELL_H - PROBLEM_FONT_SIZE - 12
        c.setFillColor(colors.HexColor("#1a1a1a"))
        c.drawString(cell_x + 14, text_y, problem_text)

        # --- Counting rectangle ---
        rect_x = cell_x + 14
        rect_y = cell_y + 14
        rect_w = CELL_W - 28
        c.setStrokeColor(colors.HexColor("#555555"))
        c.setLineWidth(1.2)
        c.setFillColor(colors.HexColor("#fafafa"))
        c.roundRect(rect_x, rect_y, rect_w, RECT_HEIGHT,
                    RECT_CORNER_RADIUS, stroke=1, fill=1)

        # Light vertical guide lines inside rectangle (evenly spaced)
        num_guides = 18
        guide_spacing = rect_w / (num_guides + 1)
        c.setStrokeColor(colors.HexColor("#dddddd"))
        c.setLineWidth(0.5)
        for g in range(1, num_guides + 1):
            gx = rect_x + g * guide_spacing
            c.line(gx, rect_y + 5, gx, rect_y + RECT_HEIGHT - 5)

    if show_page_num:
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#888888"))
        c.drawCentredString(PAGE_W / 2, 22, f"Page {page_num}")


def generate_worksheet(
    output_path: str = "math_worksheet.pdf",
    num_pages: int = 4,
    op_mix: str = "both",
    title: str = "Math Practice",
    show_page_numbers: bool = True,
    seed: int | None = None,
) -> str:
    if seed is not None:
        random.seed(seed)

    total_problems = num_pages * PROBLEMS_PER_PAGE
    all_problems = make_problems(total_problems, op_mix)

    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(title)
    c.setAuthor("Math Worksheet Generator")

    for page in range(num_pages):
        start = page * PROBLEMS_PER_PAGE
        page_problems = all_problems[start: start + PROBLEMS_PER_PAGE]
        draw_page(c, page_problems, page + 1, title, show_page_numbers)
        c.showPage()

    c.save()
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate printable A4 math worksheets for kids."
    )
    parser.add_argument("-o", "--output", default="math_worksheet.pdf",
                        help="Output PDF filename (default: math_worksheet.pdf)")
    parser.add_argument("-p", "--pages", type=int, default=4,
                        help="Number of pages to generate (default: 4)")
    parser.add_argument("--ops", choices=["add", "sub", "both"], default="both",
                        help="Which operations to include (default: both)")
    parser.add_argument("--title", default="Math Practice",
                        help="Worksheet title shown on each page")
    parser.add_argument("--no-page-numbers", action="store_true",
                        help="Omit page numbers from footer")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible worksheets")
    args = parser.parse_args()

    path = generate_worksheet(
        output_path=args.output,
        num_pages=args.pages,
        op_mix=args.ops,
        title=args.title,
        show_page_numbers=not args.no_page_numbers,
        seed=args.seed,
    )
    print(f"Saved: {path}  ({args.pages} pages, {args.pages * PROBLEMS_PER_PAGE} problems)")


if __name__ == "__main__":
    main()
