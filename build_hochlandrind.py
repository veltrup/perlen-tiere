#!/usr/bin/env python3
"""Erzeugt eine kindgerechte Anleitung (HTML mit SVG-Skizzen) für das Perlen-Hochlandrind.
Danach mit Chrome headless in PDF umwandeln (siehe make_pdf.sh)."""
import math
import random
from pathlib import Path

# ---------- Farben ----------
H = '#C98B4F'    # hellbraun
D = '#6B3A1F'    # dunkelbraun
M = '#9C5A2C'    # mittelbraun
CR = '#F2E2BF'   # cremeweiß
BK = '#262626'   # schwarz
OLD = '#BDB4AA'  # "alte" Perle in Technik-Skizzen
BLUE = '#1F6FD6'
RED = '#E0442B'
PLUS = '#3E9B4F'
MINUS = '#E2832B'


def darker(c, f=0.62):
    c = c.lstrip('#')
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02x%02x%02x' % (int(r * f), int(g * f), int(b * f))


# ---------- SVG-Bausteine ----------
def bead(x, y, r, fill, new=False, ghost=False, num=None):
    s = ''
    if new:
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r + 5:.1f}" fill="#FFE36E" opacity=".55"/>'
    if ghost:
        return s + (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="{darker(fill)}" '
                    f'stroke-width="2" stroke-dasharray="4 3"/>')
    s += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{darker(fill)}" '
          f'stroke-width="{max(0.8, r * 0.12):.2f}"/>'
          f'<circle cx="{x - r * .35:.1f}" cy="{y - r * .38:.1f}" r="{r * .3:.1f}" fill="#fff" opacity=".5"/>')
    if num is not None:
        col = '#fff' if fill in (D, BK, M) else '#3a2a1a'
        s += (f'<text x="{x:.1f}" y="{y + r * .38:.1f}" text-anchor="middle" font-size="{r * 1.05:.1f}" '
              f'font-weight="700" fill="{col}">{num}</text>')
    return s


def thread(pts, color, arrow=True, width=3.2, dash=None):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    mk = f' marker-end="url(#ah-{"b" if color == BLUE else "r" if color == RED else "g"})"' if arrow else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" '
            f'stroke-linecap="round" opacity=".92"{mk}{da}/>')


def text(x, y, t, size=13, color='#333', anchor='middle', weight=600):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{t}</text>')


def svg(w, h, body, cls='', style='', vb=None):
    vb = vb or f'0 0 {w} {h}'
    return (f'<svg viewBox="{vb}" class="{cls}" style="{style}" xmlns="http://www.w3.org/2000/svg">'
            f'{body}</svg>')


DEFS = f'''<svg width="0" height="0" style="position:absolute"><defs>
<marker id="ah-b" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>
<marker id="ah-r" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>
<marker id="ah-g" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#777"/></marker>
</defs></svg>'''


def mid(p, q):
    return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)


# ---------- Hochlandrind-Illustration ----------
def hex_fill(cx, cy, rx, ry, palette, weights, rng, r=6.0, sp=12.4, rot=0.0):
    out = []
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = max(rx, ry)
    row = 0
    y = -R
    while y <= R:
        x = -R + (sp / 2 if row % 2 else 0)
        while x <= R:
            if (x / rx) ** 2 + (y / ry) ** 2 <= 1:
                px = cx + x * ca - y * sa
                py = cy + x * sa + y * ca
                out.append(bead(px, py, r, rng.choices(palette, weights)[0]))
            x += sp
        y += sp * 0.866
        row += 1
    return ''.join(out)


def quad(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])


def cow_body(seed=7):
    rng = random.Random(seed)
    s = '<ellipse cx="200" cy="402" rx="150" ry="16" fill="#000" opacity=".10"/>'
    # Schwanz (hinter dem Körper)
    for i in range(10):
        x, y = quad((285, 330), (345, 330), (348, 262), i / 9)
        s += bead(x, y, 6.5, D)
    for a in (-60, -100, -140):
        for k in (1, 2, 3):
            s += bead(348 + math.cos(math.radians(a)) * 9 * k, 262 + math.sin(math.radians(a)) * 9 * k, 5.5, D)
    # Hinterbeine
    s += hex_fill(98, 372, 44, 22, [D, M], [3, 1], rng)
    s += hex_fill(302, 372, 44, 22, [D, M], [3, 1], rng)
    # Körper
    s += hex_fill(200, 300, 112, 88, [M, D, H], [5, 3, 2], rng)
    # Vorderbeine
    s += hex_fill(156, 352, 26, 44, [D, M], [3, 1], rng)
    s += hex_fill(244, 352, 26, 44, [D, M], [3, 1], rng)
    # Hörner
    for side in (-1, 1):
        p0, p1, p2 = (200 + side * 62, 128), (200 + side * 150, 128), (200 + side * 140, 52)
        for i in range(13):
            t = i / 12
            x, y = quad(p0, p1, p2, t)
            s += bead(x, y, 11 - 6 * t, CR if i < 10 else '#E3CC9C')
    # Ohren
    s += hex_fill(92, 178, 42, 19, [M, H], [2, 1], rng, rot=18)
    s += hex_fill(308, 178, 42, 19, [M, H], [2, 1], rng, rot=-18)
    # Kopf
    s += hex_fill(200, 182, 96, 86, [M, D, H], [5, 3, 2], rng)
    # Augen
    for ex in (158, 242):
        s += f'<circle cx="{ex}" cy="185" r="10" fill="{BK}"/><circle cx="{ex - 3}" cy="181" r="3.2" fill="#fff"/>'
    # Stirnhaare
    hair = [H, M, '#B8763C', D]
    for i, x0 in enumerate(range(116, 290, 13)):
        top = 182 - 86 * math.sqrt(max(0, 1 - ((x0 - 200) / 96) ** 2)) + 8
        n = 7 if abs(x0 - 200) < 50 else 5
        for k in range(n):
            x = x0 + math.sin(k * 0.9 + i) * 3 + (x0 - 200) * 0.04 * k
            y = top + k * 10.5
            if y > 168 and min(abs(x - 158), abs(x - 242)) < 20:
                break
            s += bead(x, y, 6.2, rng.choice(hair))
    # Maul + Nase
    s += hex_fill(200, 232, 58, 36, [CR, '#E8D3A8'], [4, 1], rng, r=6.2)
    s += bead(181, 236, 8, BK) + bead(219, 236, 8, BK)
    return s


# ---------- Technik-Skizzen ----------
L = 56          # Seitenlänge einer Masche
YB = 132        # Unterkante (alte Perlen)
RB = 13         # Perlenradius in Technik-Skizzen


def startkreis_panels():
    a = '<line x1="10" y1="70" x2="110" y2="70" stroke="%s" stroke-width="3.2"/>' % BLUE
    a += '<line x1="110" y1="70" x2="210" y2="70" stroke="%s" stroke-width="3.2"/>' % RED
    for i in range(5):
        a += bead(66 + i * 22, 70, 10.5, H, num=i + 1)
    a += text(30, 55, 'Blau', 12, BLUE) + text(190, 55, 'Rot', 12, RED)
    a += text(110, 110, '← 1 m →  · 5 Perlen ·  ← 1 m →', 11, '#777', weight=500)

    def ring(extra=''):
        cx, cy, rr = 110, 62, 34
        angs = [54, 342, 270, 198, 126]   # Perle 1..5, Lücke unten
        s = f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="#999" stroke-width="2"/>'
        for i, ag in enumerate(angs):
            s += bead(cx + rr * math.cos(math.radians(ag)), cy + rr * math.sin(math.radians(ag)), 12, H,
                      num=i + 1, new=(extra == 'hl' and i == 0))
        return s

    b = ring()
    b += thread([(110, 96), (80, 128)], BLUE, arrow=False) + thread([(110, 96), (140, 128)], RED, arrow=False)
    b += '<circle cx="110" cy="98" r="6" fill="#555"/>' + text(150, 104, '2 Knoten', 12, '#555', 'start')

    c = ring('hl')
    pts = [(110 + 34 * math.cos(math.radians(a_)), 62 + 34 * math.sin(math.radians(a_))) for a_ in (90, 54, 20)]
    pts.append((110 + 58 * math.cos(math.radians(14)), 62 + 58 * math.sin(math.radians(14))))
    c += thread([(110, 96)] + pts, BLUE)
    c += thread([(110, 96), (84, 126)], RED, arrow=False)
    c += '<circle cx="110" cy="98" r="5" fill="#555"/>'
    c += text(186, 112, 'Perle 1', 12, '#8a6d00')
    return [svg(220, 135, a), svg(220, 135, b), svg(220, 135, c)]


def unit_beads(x0, done=True, top_new=False, side_new=False):
    """Fertige Masche zwischen Ecken x0 und x0+L."""
    s = bead(x0 + L / 2, YB, RB, OLD)
    s += bead(x0, YB - L / 2, RB, H)
    s += bead(x0 + L / 2, YB - L, RB, H)
    s += bead(x0 + L, YB - L / 2, RB, H)
    return s


def masche_panels():
    x1 = 22  # linke Ecke Masche 1
    base = unit_beads(x1)
    base += bead(x1 + L * 1.5, YB, RB, OLD) + bead(x1 + L * 2.5, YB, RB, OLD)
    xc, xn = x1 + L, x1 + 2 * L   # Ecken der neuen Masche
    top, bot = YB - L, YB
    # 1: untere Schnur durch alte Perle
    p1 = base
    p1 += thread([(xc, bot - 18), (xc, bot), (xn + 6, bot)], BLUE)
    p1 += thread([(xc, top + 18), (xc, top), (xc + 8, top - 12)], RED, arrow=False)
    # 2: obere Schnur nimmt 2 neue
    p2 = base + bead(xc + L / 2, top, RB, H, new=True) + bead(xn, YB - L / 2, RB, H, new=True)
    p2 += thread([(xc, bot - 18), (xc, bot), (xn, bot)], BLUE, arrow=False)
    p2 += thread([(xc, top + 18), (xc, top), (xn, top), (xn, bot - 12)], RED)
    # 3: kreuzen
    p3 = base + bead(xc + L / 2, top, RB, H) + bead(xn, YB - L / 2, RB, H)
    p3 += thread([(xc, bot - 18), (xc, bot), (xn, bot), (xn, top - 14)], BLUE)
    p3 += thread([(xc, top + 18), (xc, top), (xn, top), (xn, bot + 14)], RED)
    p3 += '<circle cx="%s" cy="%s" r="22" fill="none" stroke="#F5B400" stroke-width="2.5" stroke-dasharray="5 4"/>' % (xn, YB - L / 2)
    # 4: fertig
    p4 = base + bead(xc + L / 2, top, RB, H) + bead(xn, YB - L / 2, RB, H)
    p4 += thread([(xn, top + 4), (xn + 10, top - 12)], BLUE, arrow=False)
    p4 += thread([(xn, bot - 4), (xn + 10, bot + 12)], RED, arrow=False)
    p4 += text(xn + 14, top - 14, 'oben', 13, BLUE, 'start') + text(xn + 14, bot + 22, 'unten', 13, RED, 'start')
    return [svg(205, 110, p, vb='0 50 205 110') for p in (p1, p2, p3, p4)]


def erste_masche_panels():
    base = ''
    for k in range(3):
        base += bead(54 + L / 2 + k * L, YB, RB, OLD, num=k + 1)
    xa, xb = 54, 54 + L
    top = YB - L
    p1 = base + thread([(xa - 12, YB + 20), (xa, YB)], RED, arrow=False) + thread([(xb + 12, YB + 20), (xb, YB)], BLUE, arrow=False)
    p1 += bead(xa, YB - L / 2, RB, H, new=True) + bead(xa + L / 2, top, RB, H, new=True) + bead(xb, YB - L / 2, RB, H, new=True)
    p1 += thread([(xa - 12, YB + 20), (xa, YB), (xa, top), (xb, top), (xb, YB - 10)], RED)
    p2 = base + bead(xa, YB - L / 2, RB, H) + bead(xa + L / 2, top, RB, H) + bead(xb, YB - L / 2, RB, H)
    p2 += thread([(xa - 12, YB + 20), (xa, YB), (xa, top), (xb, top), (xb, YB + 16)], RED)
    p2 += thread([(xb + 12, YB + 20), (xb, YB), (xb, top - 16)], BLUE)
    return [svg(220, 120, p1, vb='10 45 220 120'), svg(220, 120, p2, vb='10 45 220 120')]


def zunahme_svg():
    x1 = 22
    s = unit_beads(x1)
    xc = x1 + L
    tl, tm, tr = (xc, YB - L), (xc + 46, YB - L), (xc + 92, YB - L)
    bl, br = (xc, YB), (xc + L, YB)
    s += bead(*mid(bl, br), RB, OLD)
    s += bead(*mid(tl, tm), RB, H, new=True) + bead(*mid(tm, tr), RB, H, new=True) + bead(*mid(tr, br), RB, H, new=True)
    s += thread([(xc, YB - L + 18), tl, tm, tr, (br[0] + 4, br[1] + 12)], RED)
    s += thread([(xc, YB - 18), bl, br, (tr[0] + 5, tr[1] - 10)], BLUE)
    s += text(xc + 46, YB - L - 22, '2 Perlen oben!', 12, PLUS)
    return svg(220, 125, s, vb='0 40 220 125')


def abnahme_svg():
    x1 = 22
    s = unit_beads(x1)
    xc = x1 + L
    tl, tr = (xc, YB - L), (xc + L, YB - L)
    b1, b2, b3 = (xc, YB), (xc + L, YB), (xc + 2 * L, YB)
    s += bead(*mid(b1, b2), RB, OLD) + bead(*mid(b2, b3), RB, OLD)
    s += bead(*mid(tl, tr), RB, H, new=True) + bead(*mid(tr, b3), RB, H, new=True)
    s += thread([(xc, YB - L + 18), tl, tr, (b3[0] + 8, b3[1] + 10)], RED)
    s += thread([(xc, YB - 18), b1, b2, b3, (tr[0] - 6, tr[1] - 10)], BLUE)
    s += text(xc + L, YB + 26, '2 alte Perlen auf einmal', 12, MINUS)
    return svg(230, 125, s, vb='0 45 230 125')


def schliessen_svg():
    s = ''
    x = 30
    for k in range(2):
        s += unit_beads(x + k * L)
    s += text(x + 2 * L + 34, YB - L / 2 + 5, '…', 26, '#888')
    xl = x + 2 * L + 70
    s += bead(xl, YB - L / 2, RB, H)          # Seitenperle der vorletzten Masche
    s += bead(xl + L / 2, YB, RB, OLD)
    s += bead(xl + L / 2, YB - L, RB, H, new=True)
    xg = xl + L
    s += bead(xg, YB - L / 2, RB, H, ghost=True)
    s += thread([(xl, YB - L + 18), (xl, YB - L), (xg, YB - L), (xg, YB + 14)], RED)
    s += thread([(xl, YB - 18), (xl, YB), (xg, YB), (xg, YB - L - 14)], BLUE)
    s += (f'<path d="M{xg},{YB - L - 22} C{xg - 20},{YB - L - 70} {x + 30},{YB - L - 70} {x + 4},{YB - L / 2 - 20}" '
          f'fill="none" stroke="#777" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#ah-g)"/>')
    s += text((x + xg) / 2, YB - L - 60, 'Das ist dieselbe Perle: Seitenperle 1!', 12, '#555')
    s += '<circle cx="%s" cy="%s" r="20" fill="none" stroke="#F5B400" stroke-width="2.5" stroke-dasharray="5 4"/>' % (x, YB - L / 2)
    s += text(x, YB + 32, 'Seitenperle 1', 11, '#8a6d00')
    return svg(350, 185, s, vb='-20 0 350 185')


def hochsteigen_svg():
    x1 = 50
    s = unit_beads(x1)
    s += bead(x1 + L * 1.5, YB, RB, OLD) + bead(x1 + L * 1.5, YB - L, RB, H)
    s += bead(x1 + 2 * L, YB - L / 2, RB, H)
    s = s.replace(bead(x1 + L / 2, YB - L, RB, H), bead(x1 + L / 2, YB - L, RB, H, new=True))
    s += thread([(x1, YB - L + 14), (x1, YB - L), (x1 - 10, YB - L - 14)], RED, arrow=False)
    s += thread([(x1, YB - 14), (x1, YB), (x1 + L, YB), (x1 + L, YB - L), (x1 + L + 10, YB - L - 16)], BLUE)
    s += text(x1 + L / 2, YB - L - 26, 'Perle 1 der neuen Runde', 12, '#8a6d00')
    return svg(220, 125, s, vb='10 35 220 125')


# ---------- Reihen-Kreuzen (flache Teile) ----------
def reihen_panels():
    def row(y, n, fill, new=False):
        return ''.join(bead(100 + (j - (n - 1) / 2) * 24, y, 11, fill, new=new) for j in range(n))
    a = row(132, 3, CR) + thread([(70, 132), (36, 132), (24, 110)], BLUE, arrow=False) + thread([(130, 132), (164, 132), (176, 110)], RED, arrow=False)
    a += thread([(70, 132), (130, 132)], '#999', arrow=False, width=2)
    b = row(132, 3, CR) + row(104, 3, CR, new=True)
    b += thread([(130, 132), (150, 132), (150, 104), (60, 104)], RED)
    b += thread([(70, 132), (50, 132), (40, 112)], BLUE, arrow=False)
    c = row(132, 3, CR) + row(104, 3, CR)
    c += thread([(130, 132), (150, 132), (150, 104), (50, 104), (40, 92)], RED)
    c += thread([(70, 132), (50, 132), (50, 104), (150, 104), (160, 92)], BLUE)
    for p in (a, b, c):
        pass
    return [svg(180, 75, x, vb='10 78 180 75') for x in (a, b, c)]


def rows_svg(rows, colors, w=180, r=10.5, label_rows=True, note_bottom=None):
    n = len(rows)
    h = n * (2 * r + 3) + 40
    s = ''
    for i, (cnt, cols) in enumerate(zip(rows, colors)):
        y = h - 28 - i * (2 * r + 3)
        for j in range(cnt):
            s += bead(w / 2 + (j - (cnt - 1) / 2) * (2 * r + 2), y, r, cols[j % len(cols)])
        if label_rows:
            s += text(16, y + 4, f'R{i + 1}', 10, '#999', 'start', 500)
    if note_bottom:
        s += text(w / 2, h - 4, note_bottom, 10.5, '#777', weight=500)
    return svg(w, h, s), h


def horn_curved_svg():
    rows = [3, 3, 2, 2, 2, 1, 1, 1]
    s = ''
    cx0, y0, R = 70, 190, 150
    for i, n in enumerate(rows):
        th = i * 0.15
        c = (cx0 + R * (1 - math.cos(th)), y0 - R * math.sin(th))
        nrm = (math.cos(th), math.sin(th))
        for j in range(n):
            off = (j - (n - 1) / 2) * 21
            s += bead(c[0] + nrm[0] * off, c[1] + nrm[1] * off, 10, CR if i < 5 else '#E3CC9C')
    s += (f'<path d="M30,170 C28,120 50,80 95,50" fill="none" stroke="#777" stroke-width="2" '
          f'marker-end="url(#ah-g)" stroke-dasharray="5 4"/>')
    s += text(105, 218, "eine Seite fester ziehen", 11, '#777', weight=500)
    return svg(210, 225, s)


def ohr_svg():
    s, _ = rows_svg([1, 2, 3], [[D], [H, H], [H, D, H]], w=150, note_bottom='')
    return s


def nase_svg():
    cx, cy, rx, ry = 110, 84, 62, 44
    s = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="#aaa" stroke-width="2"/>'
    s += bead(cx - 30, cy, 9, BK, ghost=True) + bead(cx + 30, cy, 9, BK, ghost=True)
    for i in range(12):
        a = math.radians(-90 + i * 30)
        s += bead(cx + rx * math.cos(a), cy + ry * math.sin(a), 11, CR, num=i + 1)
    s += thread([(cx, cy - ry + 10), (cx, cy + ry - 10)], RED, arrow=False, width=2.5)
    s += bead(cx, cy - 13, 11, CR, new=True) + bead(cx, cy + 13, 11, CR, new=True)
    s += text(cx - 30, cy - 16, 'Loch', 10, '#777', weight=600) + text(cx + 30, cy - 16, 'Loch', 10, '#777', weight=600)
    return svg(220, 150, s)


def bein_svg():
    s, _ = rows_svg([3, 3, 3, 3, 2, 1], [[D]] * 6, w=150, r=10)
    return s


def schwanz_svg():
    s = ''
    for i in range(10):
        s += bead(22 + i * 21, 80, 10, D, num=i + 1 if i in (0, 9) else None)
    bx = 22 + 9 * 21
    for a in (-65, 0, 65):
        for da, dist in ((-13, 32), (0, 54), (13, 32)):
            ar = math.radians(a + da)
            s += bead(bx + math.cos(ar) * dist, 80 + math.sin(ar) * dist, 9, D, new=True)
    s += text(bx - 60, 150, '3 Schlaufen = Quaste', 13, PLUS)
    return svg(285, 160, s)


def haar_svg():
    rng = random.Random(3)
    s = ''
    for i, (n, label) in enumerate(((6, 'kurz'), (8, 'lang'))):
        x = 45 + i * 90
        s += (f'<path d="M{x},6 C{x + 8},40 {x - 8},100 {x},{40 + n * 15}" fill="none" stroke="#8B5A2B" '
              f'stroke-width="4" stroke-linecap="round"/>')
        for k in range(n):
            y = 40 + k * 15
            s += bead(x + math.sin(k * 0.9) * 3, y, 7.5, rng.choice([H, M, D, '#B8763C']))
        s += f'<circle cx="{x}" cy="{42 + n * 15}" r="6" fill="#5a3a1a"/>'
        s += text(x, 190, f'{n} Perlen', 11, '#333')
        s += text(x, 205, '4× vorne' if n == 6 else '6× Seiten + hinten', 10.5, '#8a6d00', weight=600)
    s += text(150, 22, '← 3 cm frei', 11, '#777', 'start', 500)
    s += text(90, 160, 'Knoten', 10.5, '#5a3a1a')
    return svg(240, 212, s)


def frisur_top_svg():
    """Kopf von oben: 10 Strähnen strahlen von der Öffnung aus."""
    cx, cy, R = 150, 128, 100
    s = ''
    # Ohren seitlich, Kopf, Hörner hinten seitlich, Maul vorne
    for ea in (10, 170):
        a = math.radians(ea)
        s += (f'<ellipse cx="{cx + (R + 14) * math.cos(a):.0f}" cy="{cy + (R + 14) * math.sin(a):.0f}" rx="22" ry="12" '
              f'fill="{M}" stroke="{darker(M)}" stroke-width="2"/>')
    s += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#d9b48e" stroke="{darker("#d9b48e")}" stroke-width="2"/>'
    for ang in (-40, -140):
        a = math.radians(ang)
        for k in range(6):
            rr = R - 6 + k * 12
            s += bead(cx + rr * math.cos(a), cy + rr * math.sin(a), 8.5 - k * 0.7, CR)
    s += f'<ellipse cx="{cx}" cy="{cy + R + 4}" rx="44" ry="20" fill="{CR}" stroke="{darker(CR)}" stroke-width="2"/>'
    # Strähnen
    plan = [(a, 6) for a in (62, 81, 99, 118)] + [(a, 8) for a in (150, 205, 30, -25, 245, 295)]
    for i, (ang, n) in enumerate(plan):
        a = math.radians(ang)
        cols = [H, '#B8763C', H, M] if i % 2 == 0 else [D, M, D, '#B8763C']
        s += (f'<line x1="{cx + 14 * math.cos(a):.0f}" y1="{cy + 14 * math.sin(a):.0f}" '
              f'x2="{cx + (20 + (n - 1) * 11) * math.cos(a):.0f}" y2="{cy + (20 + (n - 1) * 11) * math.sin(a):.0f}" '
              f'stroke="#8B5A2B" stroke-width="3"/>')
        for k in range(n):
            rr = 22 + k * 11
            s += bead(cx + rr * math.cos(a), cy + rr * math.sin(a), 5.6, cols[k % 4])
    # Öffnung (6 Perlen von Runde 15)
    for k in range(6):
        a = math.radians(k * 60)
        s += bead(cx + 11 * math.cos(a), cy + 11 * math.sin(a), 5.5, D)
    s += text(cx, cy + R + 44, 'vorne = Gesicht ↓', 12.5, '#5a2f14', weight=700)
    s += text(cx, 12, 'hinten', 12, '#777', weight=600)
    s += f'<line x1="{cx - 22}" y1="{cy + 70}" x2="{cx - 120}" y2="{cy + 112}" stroke="#333" stroke-width="1.2" stroke-dasharray="3 3"/>'
    s += text(cx - 150, cy + 126, '4 kurze vorne', 11, '#333', 'start')
    s += f'<line x1="{cx - 90}" y1="{cy - 30}" x2="{cx - 132}" y2="{cy - 60}" stroke="#333" stroke-width="1.2" stroke-dasharray="3 3"/>'
    s += text(cx - 148, cy - 66, 'lange', 11, '#333', 'start')
    return svg(300, 290, s, vb='0 0 300 290')


def frisur_knoten_svg():
    s = ''
    for k, x in enumerate((50, 100, 150)):
        s += bead(x, 60 + (12 if k != 1 else 0), 16, D)
    # Wolle: von der Strähne hoch, durch die mittlere Perle, Doppelknoten
    s += ('<path d="M100,160 C100,120 92,100 92,72 M108,72 C108,52 96,40 104,30" fill="none" '
          'stroke="#8B5A2B" stroke-width="4" stroke-linecap="round"/>')
    s += '<path d="M92,72 L108,72" stroke="#8B5A2B" stroke-width="4" stroke-dasharray="3 3" opacity=".7"/>'
    s += '<circle cx="104" cy="28" r="7" fill="#5a3a1a"/><path d="M104,28 l-14,-12 M104,28 l12,-14" stroke="#8B5A2B" stroke-width="3"/>'
    for k in range(3):
        s += bead(100, 112 + k * 16, 7.5, [H, M, D][k])
    s += text(120, 26, 'Doppelknoten', 11, '#5a3a1a', 'start')
    s += text(176, 78, 'Perle der', 10.5, '#777', 'start', 500) + text(176, 91, 'Öffnung', 10.5, '#777', 'start', 500)
    s += text(118, 150, 'Strähne', 10.5, '#777', 'start', 500)
    return svg(220, 160, s, vb='20 10 220 160')


def frisur_vorne_svg():
    return svg(340, 250, cow_body(seed=7), vb='30 30 340 250')


def material_svg():
    s = ''
    # Schnur-Rolle
    s += '<ellipse cx="40" cy="45" rx="28" ry="28" fill="#dfe9f3" stroke="#8aa3bd" stroke-width="2"/>'
    s += '<circle cx="40" cy="45" r="9" fill="#fff" stroke="#8aa3bd" stroke-width="2"/>'
    s += '<path d="M66,52 C90,60 95,80 120,82" stroke="#8aa3bd" stroke-width="2" fill="none"/>'
    s += text(40, 95, 'Angelschnur', 11)
    # Perlen-Schälchen
    for i, (c, n) in enumerate([(H, 'hellbraun'), (D, 'dunkelbraun'), (CR, 'cremeweiß'), (BK, 'schwarz')]):
        x = 155 + i * 70
        s += f'<path d="M{x - 28},40 Q{x},78 {x + 28},40 Z" fill="#f4f1ec" stroke="#bbb" stroke-width="2"/>'
        for j in range(5):
            s += bead(x - 14 + j * 7, 44 + (j % 2) * 5, 5.5, c)
        s += text(x, 95, n, 11)
    # Wolle
    s += '<circle cx="455" cy="45" r="25" fill="#9C5A2C"/>'
    for k in range(5):
        s += f'<path d="M{432 + k * 2},{30 + k * 7} Q455,{20 + k * 9} {478 - k},{34 + k * 7}" stroke="#7a431d" stroke-width="2" fill="none"/>'
    s += text(455, 95, 'Wolle', 11)
    # Watte
    s += '<g fill="#fff" stroke="#ccc" stroke-width="2"><circle cx="525" cy="50" r="15"/><circle cx="545" cy="40" r="17"/><circle cx="563" cy="52" r="14"/></g>'
    s += text(545, 95, 'Watte', 11)
    # Pinzette
    s += '<path d="M600,20 L640,72 M612,18 L644,70" stroke="#888" stroke-width="4" stroke-linecap="round"/>'
    s += text(625, 95, 'Pinzette', 11)
    # Schere
    s += ('<circle cx="672" cy="66" r="9" fill="none" stroke="#d24" stroke-width="4"/>'
          '<circle cx="694" cy="66" r="9" fill="none" stroke="#d24" stroke-width="4"/>'
          '<path d="M676,58 L700,18 M690,58 L666,18" stroke="#888" stroke-width="4" stroke-linecap="round"/>')
    s += text(683, 95, 'Schere', 11)
    # Klebeband
    s += f'<rect x="725" y="30" width="34" height="14" rx="2" fill="{BLUE}" opacity=".8" transform="rotate(-10 742 37)"/>'
    s += f'<rect x="725" y="54" width="34" height="14" rx="2" fill="{RED}" opacity=".8" transform="rotate(8 742 61)"/>'
    s += text(742, 95, 'Klebeband', 11)
    return svg(780, 105, s)


# ---------- Runden-Plan ----------
# Zeichen: n = normale Masche, p = Zunahme (+), m = Abnahme (−)
RUNDEN = [
    # (Runde, Bereich, Maschenfolge, Perlen danach, Hinweis)
    (2, 'Körper', 'ppppp', 10, 'Jede Masche ist eine Plus-Masche.'),
    (3, 'Körper', 'npnpnpnpnp', 15, 'Binde an Masche 1, 4, 6 und 9 einen Wollfaden: Hier kommen später die Beine hin.'),
    (4, 'Körper', 'nnp' * 5, 20, 'Jetzt ist der Bauch schon richtig breit.'),
    (5, 'Körper', 'n' * 20, 20, 'Ab jetzt wächst der Rand nach oben. Merke dir Masche 15 – hier kommt später der Schwanz hin.'),
    (6, 'Körper', 'n' * 20, 20, ''),
    (7, 'Hals', 'nnm' * 5, 15, 'Jetzt wird es schmaler.'),
    (8, 'Hals', 'nnnm' * 3, 12, 'Der Hals ist am schmalsten.'),
    (9, 'Kopf', 'nnpnnnnnpnnn', 14, ''),
    (10, 'Kopf', 'nnnpnnnnnnpnnn', 16, ''),
    (11, 'Kopf', 'nnnpnnnnnnnpnnnn', 18, ''),
    (12, 'Kopf', 'nnnnpnnnnnnnnpnnnn', 20, 'Der Kopf ist jetzt am breitesten.'),
    (13, 'Kopf', 'nnm' * 5, 15, ''),
    (14, 'Kopf', 'nm' * 5, 10, ''),
    (15, 'Kopf', 'nmmnmm', 6, 'Das ist die Öffnung oben. Schnur NICHT abschneiden!'),
]


def check_runden():
    prev = 5
    for r, _, seq, after, _ in RUNDEN:
        used = sum(2 if c == 'm' else 1 for c in seq)
        made = sum(2 if c == 'p' else 1 for c in seq)
        assert used == prev, (r, used, prev)
        assert made == after, (r, made, after)
        prev = after


def new_beads(seq):
    """Neue Perlen pro Runde nach der Tabelle erste/mitte/letzte."""
    n = 0
    for i, c in enumerate(seq):
        base = 3 if i == 0 else 1 if i == len(seq) - 1 else 2
        n += base + (1 if c == 'p' else 0)
    return n


def seq_svg(seq):
    sz, gap = 22, 4
    w = len(seq) * (sz + gap)
    s = ''
    for i, c in enumerate(seq):
        x = i * (sz + gap) + sz / 2
        fill = {'n': H, 'p': PLUS, 'm': MINUS}[c]
        s += f'<circle cx="{x}" cy="12" r="10.5" fill="{fill}" stroke="{darker(fill)}" stroke-width="1.2"/>'
        sym = {'n': '', 'p': '+', 'm': '−'}[c]
        if sym:
            s += f'<text x="{x}" y="17.5" font-size="16" font-weight="800" fill="#fff" text-anchor="middle">{sym}</text>'
        s += f'<text x="{x}" y="34" font-size="8.5" fill="#999" text-anchor="middle">{i + 1}</text>'
    return svg(w, 38, s, style=f'width:{w * 0.92:.0f}px')


def profil_svg():
    counts = [5] + [r[3] for r in RUNDEN]
    rng = random.Random(11)
    rr, step = 5.2, 11.2
    h = len(counts) * 15 + 50
    s = ''
    for i, c in enumerate(counts):
        y = h - 28 - i * 15
        w = c * step
        for j in range(c):
            s += bead(175 - w / 2 + step / 2 + j * step, y, rr, H if i == 0 else rng.choice([H, M, D]))
        s += text(20, y + 4, f'R{i + 1}', 10.5, '#888', 'start', 600)
        s += text(312, y + 4, f'{c}', 10.5, '#555', 'end', 700)
    # Bereiche
    def brace(i0, i1, label, col):
        y0 = h - 28 - i1 * 15 - 7
        y1 = h - 28 - i0 * 15 + 7
        return (f'<path d="M322,{y0} q8,0 8,8 L330,{(y0 + y1) / 2 - 5} l6,5 l-6,5 L330,{y1 - 8} q0,8 -8,8" '
                f'fill="none" stroke="{col}" stroke-width="2"/>'
                + text(342, (y0 + y1) / 2 + 4, label, 12, col, 'start', 700))
    s += brace(0, 5, 'Körper', '#9C5A2C') + brace(6, 7, 'Hals', '#777') + brace(8, 14, 'Kopf', '#6B3A1F')
    yb = h - 28 - 2 * 15
    s += f'<text x="{175 - 15 * step / 2 - 8}" y="{yb + 4}" font-size="10" font-weight="700" fill="{PLUS}" text-anchor="end">Beine →</text>'
    yt = h - 28 - (len(counts) - 1) * 15
    s += (f'<path d="M175,{yt - 26} L175,{yt - 9}" stroke="#777" stroke-width="2" marker-end="url(#ah-g)"/>'
          + text(165, yt - 18, 'Öffnung zum Füllen', 10.5, '#777', 'end', 600))
    s += text(312, 16, 'Perlen', 9.5, '#888', 'end', 600)
    return svg(400, h, s)


def zusammenbau_svg():
    s = cow_body(seed=7)
    calls = [  # (Nr, Punkt am Rind, Position der Nummer)
        (1, (200, 98), (200, 24)),
        (2, (230, 120), (300, 18)),
        (3, (62, 70), (20, 30)),
        (4, (82, 176), (20, 150)),
        (5, (200, 232), (390, 230)),
        (6, (242, 185), (390, 160)),
        (7, (156, 380), (60, 430)),
        (8, (348, 262), (395, 300)),
        (9, (200, 98), (120, 24)),
    ]
    for n, (px, py), (tx, ty) in calls:
        s += f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty}" stroke="#333" stroke-width="1.5" stroke-dasharray="3 3"/>'
        s += f'<circle cx="{px}" cy="{py}" r="4" fill="#333"/>'
        s += (f'<circle cx="{tx}" cy="{ty}" r="15" fill="#FFD84D" stroke="#333" stroke-width="2"/>'
              f'<text x="{tx}" y="{ty + 6}" font-size="17" font-weight="800" text-anchor="middle" fill="#333">{n}</text>')
    return svg(420, 450, s)


def annaehen_svg():
    s = ''
    for k in range(5):
        s += bead(40 + k * 34, 120, 13, OLD)
    s += text(110, 152, 'Perlen am Körper', 11, '#777', weight=500)
    for k in range(3):
        s += bead(76 + k * 26, 52, 11, CR)
    s += text(102, 26, 'Teil (z. B. Horn)', 11, '#777', weight=500)
    s += thread([(63, 52), (52, 70), (57, 120), (40, 120), (24, 104)], BLUE)
    s += thread([(141, 52), (152, 70), (147, 120), (164, 120), (180, 104)], RED)
    s += '<circle cx="24" cy="100" r="5" fill="#555"/><circle cx="180" cy="100" r="5" fill="#555"/>'
    s += text(206, 90, '3 Knoten', 11, '#555', 'end')
    return svg(220, 165, s)


def fuellen_svg(small=False):
    """Schnitt durch das Rind: Perlenhülle innen hohl, wird mit Watte gefüllt."""
    rng = random.Random(5)
    s = ''
    # Watte innen
    for _ in range(26):
        x, y = rng.uniform(70, 150), rng.uniform(55, 165)
        inb = ((x - 110) / 55) ** 2 + ((y - 135) / 38) ** 2 < 1 or ((x - 110) / 42) ** 2 + ((y - 70) / 34) ** 2 < 1
        if inb:
            s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.uniform(9, 14):.0f}" fill="#fff" stroke="#ddd" stroke-width="1.5"/>'
    # Perlenhülle: Bauch (Ellipse) und Kopf (Kreis), oben offen
    def ring(cx, cy, rx, ry, n, skip):
        out = ''
        for i in range(n):
            a = 2 * math.pi * i / n - math.pi / 2
            if skip(a):
                continue
            out += bead(cx + rx * math.cos(a), cy + ry * math.sin(a), 7, [H, M, D][i % 3])
        return out
    s += ring(110, 135, 62, 44, 24, lambda a: math.sin(a) < -0.8)
    s += ring(110, 70, 48, 40, 18, lambda a: math.sin(a) < -0.93 or math.sin(a) > 0.9)
    s += f'<path d="M110,8 L110,26" stroke="#777" stroke-width="2.5" marker-end="url(#ah-g)"/>'
    s += text(170, 18, 'Öffnung', 11, '#777', weight=600)
    if not small:
        s += text(110, 205, 'Watte', 12, '#888', weight=600)
        s += '<path d="M98,198 L100,170" stroke="#aaa" stroke-width="1.5"/>'
    h = 210 if not small else 190
    return svg(220, h, s)


# ---------- HTML ----------
def card(svg_html, num, title, body, cls=''):
    return (f'<div class="card {cls}"><div class="fig">{svg_html}</div>'
            f'<div class="cap"><span class="num">{num}</span><b>{title}</b> {body}</div></div>')


def build():
    check_runden()
    sk = startkreis_panels()
    ma = masche_panels()
    em = erste_masche_panels()
    rp = reihen_panels()

    total_body = 5 + sum(new_beads(r[2]) for r in RUNDEN)

    rows_html = ''
    for r, area, seq, after, hint in RUNDEN:
        rows_html += (f'<tr><td class="rn">{r}</td><td class="area">{area}</td><td>{seq_svg(seq)}'
                      f'{"<div class=hint>" + hint + "</div>" if hint else ""}</td>'
                      f'<td class="cnt">{len(seq)}</td><td class="cnt"><b>{after}</b></td><td class="box">☐</td></tr>')

    horn_rows, _ = rows_svg([3, 3, 2, 2, 2, 1, 1, 1], [[CR]] * 5 + [['#E3CC9C']] * 3, w=150, r=10)

    css = Path(__file__).with_name('hochlandrind.css').read_text()

    pages = []
    # --- Seite 1: Titel
    pages.append(f'''
<div class="page cover">
  <div class="kicker">Perlen-Tiere · Bastelanleitung</div>
  <h1>Mein Hochlandrind<br>aus Perlen</h1>
  <p class="sub">Schritt für Schritt – mit vielen Bildern</p>
  {svg(420, 420, cow_body(), style="width:118mm;display:block;margin:4mm auto 2mm")}
  <div class="badges">
    <div><b>Alter</b>ab ca. 8 Jahren<br>mit einem Erwachsenen</div>
    <div><b>Zeit</b>ca. 4–6 Stunden<br>ruhig an mehreren Tagen</div>
    <div><b>Schwierigkeit</b><span class="stars">★★★☆☆</span></div>
  </div>
  <p class="foot">Nach der Anleitung „Perlen-Tiere – Highland Cow“, ins Deutsche übertragen und genauer erklärt.</p>
</div>''')

    # --- Seite 2: Material
    pages.append(f'''
<div class="page">
  <h2><span class="step">0</span> Das brauchst du</h2>
  {material_svg()}
  <ul class="mat">
    <li><b>Angelschnur</b> (Nylonfaden) aus dem Set</li>
    <li><b>Perlen:</b> hellbraun und dunkelbraun (Fell), cremeweiß (Hörner und Maul), schwarz (Nasenlöcher und Augen)</li>
    <li><b>Wolle</b> für die Stirnhaare · <b>Watte</b> zum Füllen</li>
    <li><b>Pinzette</b> · <b>Schere</b> · <b>Lineal</b> · kleine <b>Schälchen</b></li>
    <li>2 kleine Stücke <b>Klebeband</b> in Blau und Rot (oder 2 Farben, die du hast)</li>
  </ul>
  <p class="small">Für den Körper brauchst du ungefähr {total_body} Perlen, für alles zusammen ungefähr {total_body + 210}.</p>

  <h3>Bevor es losgeht – 5 Profi-Tipps</h3>
  <div class="tips">
    <div class="tip"><span>1</span>Sortiere die Perlen nach Farben in Schälchen. Leg ein Handtuch auf den Tisch, dann rollt nichts weg.</div>
    <div class="tip"><span>2</span>Klebe an das eine Schnurende <b style="color:{BLUE}">blaues</b> und an das andere <b style="color:{RED}">rotes</b> Klebeband. Dann sieht deine Schnur aus wie auf den Bildern!</div>
    <div class="tip"><span>3</span>Schneide die Schnurenden schräg ab. Dann rutschen sie leichter durch die Perlen.</div>
    <div class="tip"><span>4</span>Ziehe nach jeder Masche die Schnur fest – aber nicht so fest, dass sie reißt.</div>
    <div class="tip"><span>5</span>Pause? Klemme beide Schnurenden mit einer Wäscheklammer fest. So fällt nichts auseinander.</div>
  </div>
  <div class="warn"><b>Achtung:</b> Perlen sind klein. Halte sie von Babys und kleinen Geschwistern fern. Die Schere benutzt du am besten zusammen mit einem Erwachsenen.</div>

  <h3>Die Bilder verstehen</h3>
  <div class="legend">
    {svg(40, 30, bead(20, 15, 11, OLD))}<span><b>Graue Perle</b> = alte Perle (gehört schon zur Runde davor)</span>
    {svg(40, 30, bead(20, 15, 9, H, new=True))}<span><b>Leuchtende Perle</b> = neue Perle, die du jetzt auffädelst</span>
    {svg(40, 30, thread([(4, 15), (34, 15)], BLUE))}<span>Blaues Schnurende</span>
    {svg(40, 30, thread([(4, 15), (34, 15)], RED))}<span>Rotes Schnurende</span>
  </div>
</div>''')

    # --- Seite 3: Technik Startkreis + Masche
    pages.append(f'''
<div class="page">
  <h2><span class="step">A</span> Die Perlen-Technik</h2>
  <p>Das Hochlandrind wird mit <b>zwei Schnurenden gleichzeitig</b> gefädelt. Die beiden Enden laufen immer
  <b>über Kreuz</b> durch eine Perle. So entstehen lauter kleine Vierecke aus 4 Perlen.
  Ein solches Viereck heißt <b>Masche</b>.</p>

  <h3>Technik 1 · Der Startkreis</h3>
  <div class="row3">
    {card(sk[0], 1, '5 Perlen auffädeln.', 'Schneide 2 m Schnur ab. Fädle 5 hellbraune Perlen auf und schiebe sie genau in die Mitte.')}
    {card(sk[1], 2, 'Kreis machen.', 'Zieh beide Enden zusammen, sodass ein Kreis entsteht. Mache 2 feste Knoten.')}
    {card(sk[2], 3, 'Bereit machen.', 'Fädle Blau durch Perle 1. Jetzt liegen die Enden links und rechts von Perle 1.')}
  </div>

  <h3>Technik 2 · Eine normale Masche</h3>
  <p class="small">So machst du fast alle Maschen. Die Schnur, die gerade <b>unten</b> bei den alten Perlen liegt, heißt <b>untere Schnur</b>. Die andere heißt <b>obere Schnur</b>.</p>
  <div class="row2 masche">
    {card(ma[0], 1, 'Unten:', 'Die untere Schnur geht durch die <b>nächste alte Perle</b>.')}
    {card(ma[1], 2, 'Oben:', 'Die obere Schnur nimmt <b>2 neue Perlen</b> auf.')}
    {card(ma[2], 3, 'Kreuzen:', 'Die untere Schnur geht <b>von unten</b> durch die 2. neue Perle.')}
    {card(ma[3], 4, 'Festziehen!', 'Fertig ist die Masche. Die Farben haben <b>getauscht</b> – das ist richtig so!')}
  </div>
  <div class="note">Merksatz: <b>„1 alte unten – 2 neue oben – kreuzen – festziehen.“</b></div>
</div>''')

    # --- Seite 4: Technik Erste/Plus/Minus/Schließen/Hochsteigen
    pages.append(f'''
<div class="page">
  <h3>Technik 3 · Die erste Masche einer Runde</h3>
  <div class="row2">
    {card(em[0], 1, 'Drei neue:', 'Die eine Schnur nimmt <b>3 neue Perlen</b> auf: Seite, oben, Seite.')}
    {card(em[1], 2, 'Kreuzen:', 'Die andere Schnur geht <b>von unten</b> durch die 3. neue Perle. Festziehen!')}
  </div>

  <div class="row2">
    <div>
      <h3>Technik 4 · Plus-Masche <span class="pill plus">+</span></h3>
      {card(zunahme_svg(), '+', 'Mehr Perlen:', 'Wie eine normale Masche – aber die obere Schnur nimmt <b>1 Perle mehr</b>. Oben liegen dann 2 Perlen. So wird die Runde größer.')}
    </div>
    <div>
      <h3>Technik 5 · Minus-Masche <span class="pill minus">−</span></h3>
      {card(abnahme_svg(), '−', 'Weniger Perlen:', 'Wie eine normale Masche – aber die untere Schnur geht durch <b>2 alte Perlen</b>. So wird die Runde kleiner.')}
    </div>
  </div>

  <div class="row2">
    <div>
      <h3>Technik 6 · Runde schließen</h3>
      {card(schliessen_svg(), '⟲', 'Letzte Masche:', 'Die obere Schnur nimmt nur <b>1 neue Perle</b> und geht dann durch die <b>allererste Seitenperle</b> der Runde. Die untere Schnur kreuzt durch dieselbe Perle.', 'wide')}
    </div>
    <div>
      <h3>Technik 7 · Hochsteigen</h3>
      {card(hochsteigen_svg(), '↑', 'Nach oben:', 'Die untere Schnur geht durch die <b>erste alte Perle</b> und die <b>Seitenperle daneben</b> nach oben. Jetzt liegen beide Enden neben Perle 1 der neuen Runde. Weiter mit Technik 3!')}
    </div>
  </div>

  <h3>Wie viele neue Perlen nehme ich?</h3>
  <table class="nb">
    <tr><th></th><th>normale Masche</th><th>Plus-Masche <span class="pill plus">+</span></th><th>Minus-Masche <span class="pill minus">−</span></th></tr>
    <tr><td>erste Masche der Runde</td><td>3</td><td>4</td><td>–</td></tr>
    <tr><td>Maschen in der Mitte</td><td>2</td><td>3</td><td>2 <small>(unten durch 2 alte)</small></td></tr>
    <tr><td>letzte Masche der Runde</td><td>1</td><td>2</td><td>1 <small>(unten durch 2 alte)</small></td></tr>
  </table>
</div>''')

    # --- Seite 5: Runden-Plan
    pages.append(f'''
<div class="page">
  <h2><span class="step">1</span> Körper, Hals und Kopf</h2>
  <div class="p5">
    <div>
      <p>Der ganze Körper mit Kopf ist <b>ein einziges Stück</b>. Du fädelst Runde für Runde von unten nach oben,
      wie bei einem Turm. Die erste Runde ist dein <b>Startkreis</b> (Technik 1).</p>
      <div class="hollow">{fuellen_svg(small=True)}<p class="small"><b>Gut zu wissen:</b> Der Körper ist innen <b>hohl</b> – wie ein Luftballon aus Perlen. Das ist richtig so! Ganz am Ende stopfst du ihn mit Watte aus (Schritt 3). Dann wird er prall und rund wie auf dem Bild.</p></div>
      <p>So liest du den Plan: Jeder Kreis ist eine Masche. Fang immer links an.</p>
      <div class="legend small">
        {svg(26, 26, f'<circle cx="13" cy="13" r="10" fill="{H}"/>')}<span>normale Masche</span>
        {svg(26, 26, f'<circle cx="13" cy="13" r="10" fill="{PLUS}"/><text x="13" y="18.5" font-size="16" font-weight="800" fill="#fff" text-anchor="middle">+</text>')}<span>Plus-Masche</span>
        {svg(26, 26, f'<circle cx="13" cy="13" r="10" fill="{MINUS}"/><text x="13" y="18.5" font-size="16" font-weight="800" fill="#fff" text-anchor="middle">−</text>')}<span>Minus-Masche</span>
      </div>
      <p class="small">Nach jeder Runde: <b>Runde schließen</b> (Technik 6), <b>hochsteigen</b> (Technik 7), Kästchen abhaken ✔.
      Nimm für das Fell hellbraune und dunkelbraune Perlen gemischt – das sieht schön zottelig aus.</p>
    </div>
  </div>
  <h3>So sieht dein Rind von der Seite aus – Runde für Runde</h3>
  <div class="bigprofile">{profil_svg()}</div>
</div>''')

    pages.append(f'''
<div class="page">
  <h2><span class="step">1</span> Runden-Plan zum Abhaken</h2>
  <table class="plan">
    <tr><th>Runde</th><th></th><th>Maschen (von links nach rechts)</th><th>Maschen</th><th>Perlen danach</th><th>✔</th></tr>
    <tr><td class="rn">1</td><td class="area">Körper</td><td><b>Startkreis</b> aus 5 hellbraunen Perlen (Technik 1)</td><td class="cnt">–</td><td class="cnt"><b>5</b></td><td class="box">☐</td></tr>
    {rows_html}
  </table>
</div>''')

    # --- Seite 6: Kleinteile 1
    pages.append(f'''
<div class="page">
  <h2><span class="step">2</span> Die Kleinteile</h2>
  <p>Hörner, Ohren, Beine und Maul fädelst du mit einer leichteren Technik: <b>Reihe für Reihe kreuzen</b>.</p>
  <h3>Technik 8 · Reihen kreuzen</h3>
  <div class="row3">
    {card(rp[0], 1, 'Start:', 'Fädle die Perlen der 1. Reihe auf und schiebe sie in die Mitte der Schnur.')}
    {card(rp[1], 2, 'Neue Reihe:', 'Rot nimmt die Perlen der nächsten Reihe auf.')}
    {card(rp[2], 3, 'Kreuzen:', 'Blau geht <b>von der anderen Seite</b> durch dieselben Perlen. Festziehen – die neue Reihe liegt auf der alten.')}
  </div>

  <div class="parts">
    <div class="part">
      <h3>Hörner <span class="times">× 2</span></h3>
      <div class="two">{horn_rows}{horn_curved_svg()}</div>
      <ol>
        <li>Schneide <b>40 cm</b> Schnur ab.</li>
        <li>Fädle mit cremeweißen Perlen <b>8 Reihen</b>: 3 – 3 – 2 – 2 – 2 – 1 – 1 – 1 Perlen.</li>
        <li>Ziehe eine Seite etwas fester. Dann biegt sich das Horn wie eine Banane.</li>
        <li>Schnurenden <b>nicht</b> abschneiden – damit nähst du das Horn später an.</li>
      </ol>
    </div>
    <div class="part">
      <h3>Ohren <span class="times">× 2</span></h3>
      {ohr_svg()}
      <ol>
        <li>Schneide <b>30 cm</b> Schnur ab.</li>
        <li>Reihe 1: 1 dunkelbraune Perle.</li>
        <li>Reihe 2: 2 hellbraune Perlen.</li>
        <li>Reihe 3: hellbraun – dunkelbraun – hellbraun.</li>
        <li>Es entsteht ein kleines Dreieck. Die breite Seite kommt an den Kopf.</li>
      </ol>
    </div>
  </div>
</div>''')

    # --- Seite 7: Kleinteile 2
    pages.append(f'''
<div class="page">
  <div class="parts">
    <div class="part">
      <h3>Maul mit Nase <span class="times">× 1</span></h3>
      {nase_svg()}
      <ol>
        <li>Schneide <b>30 cm</b> Schnur ab und fädle <b>12 cremeweiße</b> Perlen auf.</li>
        <li>Mach einen Kreis: Beide Enden über Kreuz durch Perle 1, dann 2 Knoten. Der Kreis ist etwa <b>1,5 cm</b> groß.</li>
        <li>Fädle mit einem Ende <b>2 Perlen</b> auf und gehe durch Perle 7 auf der anderen Seite. Festziehen.</li>
        <li>Jetzt hat das Maul <b>2 Löcher</b> – das werden die Nasenlöcher.</li>
      </ol>
    </div>
    <div class="part">
      <h3>Beine <span class="times">× 4</span></h3>
      {bein_svg()}
      <ol>
        <li>Schneide für jedes Bein <b>30 cm</b> Schnur ab.</li>
        <li>Fädle mit dunkelbraunen Perlen <b>6 Reihen</b>: 3 – 3 – 3 – 3 – 2 – 1.</li>
        <li>Wenn du fest ziehst, rollt sich das Bein etwas ein und wird rund. Unten wird es spitz.</li>
        <li>Das breite Ende (Reihe 1) kommt an den Bauch.</li>
      </ol>
    </div>
    <div class="part">
      <h3>Schwanz <span class="times">× 1</span></h3>
      {schwanz_svg()}
      <ol>
        <li>Schneide <b>25 cm</b> Schnur ab und fädle <b>10 dunkelbraune</b> Perlen auf.</li>
        <li>Fädle 3 Perlen auf und gehe zurück durch Perle 10. Das ist eine Schlaufe.</li>
        <li>Mache so <b>3 Schlaufen</b>. Das ist die Quaste am Schwanz.</li>
        <li>Gehe mit der Schnur durch alle 10 Perlen zurück nach oben.</li>
      </ol>
    </div>
    <div class="part">
      <h3>Haare <span class="times">× 10</span></h3>
      {haar_svg()}
      <ol>
        <li>Schneide <b>10 Wollfäden</b> ab, jeden etwa 10 cm lang.</li>
        <li><b>4 kurze</b> Strähnen mit je <b>6 Perlen</b> (für vorne) und <b>6 lange</b> mit je <b>8 Perlen</b>. Mache 5 Strähnen mit mehr hellen und 5 mit mehr dunklen Perlen.</li>
        <li>Mache unten einen dicken Knoten. Oben bleiben etwa 3 cm frei – damit knotest du die Strähne später fest.</li>
        <li class="small">Trick: Wickle etwas Klebeband um das Wollende. Dann geht es leichter durch die Perlen.</li>
      </ol>
    </div>
  </div>
</div>''')

    # --- Seite 8: Zusammenbau
    pages.append(f'''
<div class="page">
  <h2><span class="step">3</span> Füllen und Zusammenbauen</h2>
  <div class="row-plan">
    <div>{zusammenbau_svg()}</div>
    <div>
      <h3>So nähst du ein Teil an</h3>
      {annaehen_svg()}
      <h3>Innen hohl → mit Watte füllen</h3>
      <div style="text-align:center">{fuellen_svg().replace('<svg ', '<svg style="width:38mm;height:auto" ', 1)}</div>
      <p class="small">Fädle jedes Schnurende vom Teil durch eine Perle am Körper. Dann gehst du noch einmal durch eine Perle vom Teil zurück. Mache <b>3 Knoten</b>, schneide die Schnur ab und schiebe den Knoten mit der Pinzette zwischen die Perlen.</p>
    </div>
  </div>
  <ol class="assembly">
    <li><b>Füllen:</b> Stopfe mit der Pinzette Watte durch die Öffnung oben. Nimm immer nur kleine Stücke: zuerst ganz nach unten in den Bauch, dann in den Hals und zum Schluss in den Kopf. Stopfe so lange, bis das Rind <b>prall und rund</b> ist und sich nirgends mehr eindrücken lässt – so wie auf dem Bild.</li>
    <li><b>Haare:</b> Knote die 10 Strähnen rund um die Öffnung oben fest (Runde 15). Wo welche Strähne hinkommt, steht auf der Seite <b>„Die Frisur“</b>.</li>
    <li><b>Hörner:</b> Nähe sie hinten seitlich oben am Kopf an (Runde 13–14). Sie zeigen nach außen und biegen sich nach oben.</li>
    <li><b>Ohren:</b> Nähe sie an die Seiten des Kopfes, unter die Hörner (Runde 12). Sie dürfen ein bisschen hängen.</li>
    <li><b>Maul:</b> Nähe es vorne an den Kopf (Runde 10–11). Nähe in jedes der 2 Löcher eine <b>schwarze Perle</b> – das sind die Nasenlöcher.</li>
    <li><b>Augen:</b> Nähe 2 schwarze Perlen über das Maul (Runde 12). <span class="small">(Tipp – steht nicht in der Original-Anleitung, aber man sieht sie auf dem Foto.)</span></li>
    <li><b>Beine:</b> Nähe die 4 Beine an die markierten Stellen aus Runde 3. Die Wollfäden darfst du danach abmachen.</li>
    <li><b>Schwanz:</b> Nähe ihn hinten an Runde 5 an (bei Masche 15). Er biegt sich nach oben.</li>
    <li><b>Zumachen:</b> Fädle die langen Schnurenden vom Körper noch einmal durch alle 6 Perlen von Runde 15 und ziehe fest – das Loch geht zu. Ein paarmal hin und her durch die Perlen fädeln, dann <b>3 Knoten</b>.</li>
  </ol>
  <p class="small"><b>Zum Schluss:</b> Schneide alle Schnurreste ab und stecke die Enden zwischen die Perlen. Lege die Haare in Form (siehe „Die Frisur“) und biege Hörner und Ohren vorsichtig zurecht.</p>
</div>''')

    # --- Frisur
    pages.append(f'''
<div class="page">
  <h2><span class="step">4</span> Die Frisur</h2>
  <p>Hochlandrinder haben lange, zottelige Haare. Sie fallen von oben über die Stirn – wie bei einem Wischmopp.
  Bei deinem Rind sind das die <b>10 Perlen-Strähnen</b>. Sie wachsen alle aus der <b>Mitte oben</b> auf dem Kopf.</p>
  <div class="frisur">
    <div class="card big">
      <div class="fig">{frisur_top_svg()}</div>
      <div class="cap"><span class="num">A</span><b>Von oben gesehen:</b> 4 kurze Strähnen zeigen nach vorne zum Gesicht, je 2 lange zu den Seiten und 2 lange nach hinten. In der Mitte ist die Öffnung.</div>
    </div>
    <div class="stack">
      {card(frisur_knoten_svg(), 'B', 'Festknoten:', 'Schiebe das freie Wollende mit der Pinzette durch eine Perle am Rand der Öffnung. Mache einen Doppelknoten und schneide den Rest ab.')}
      {card(frisur_vorne_svg(), 'C', 'So sieht es fertig aus:', 'Die vorderen Strähnen enden kurz über den Augen. Die Seiten reichen bis zu den Ohren.')}
    </div>
  </div>
  <h3>Schritt für Schritt</h3>
  <ol class="assembly">
    <li><b>Wann?</b> Die Haare kommen dran, wenn das Rind gefüllt ist, aber <b>bevor</b> du die Öffnung zumachst (Zusammenbau Schritt 2).</li>
    <li><b>Vorne zuerst:</b> Knote die 4 kurzen Strähnen an die Perlen der Öffnung, die zum Gesicht zeigen. Dann je 2 lange an die Seiten und 2 lange nach hinten. Die Öffnung hat nur 6 Perlen – an manche Perlen kommen also 2 Strähnen. Das ist richtig so.</li>
    <li><b>Hell und dunkel abwechseln:</b> Knote abwechselnd eine helle und eine dunkle Strähne fest. Dann sieht es aus wie auf dem Foto.</li>
    <li><b>Zumachen:</b> Wenn du die Öffnung zuziehst (Zusammenbau Schritt 9), rutschen alle Knoten in die Mitte. So entsteht oben ein schöner Haarwirbel.</li>
    <li><b>Frisieren:</b> Streiche die Strähnen mit den Fingern nach unten, sodass sie dicht auf dem Kopf liegen und schön rund fallen.</li>
  </ol>
  <div class="tips">
    <div class="tip"><span>?</span><b>Die Haare hängen über die Augen?</b> Mache den Knoten unten auf, nimm eine Perle ab und knote neu.</div>
    <div class="tip"><span>?</span><b>Eine Strähne steht ab?</b> Nähe das untere Ende mit einem Stück Angelschnur und einem kleinen Stich am Kopf fest. <em class="small">(Tipp – steht nicht im Original.)</em></div>
  </div>
</div>''')

    # --- Seite 9: Hilfe + Urkunde
    pages.append(f'''
<div class="page">
  <h2><span class="step">?</span> Hilfe-Ecke</h2>
  <div class="faq">
    <div><b>Meine Runde hat zu viele oder zu wenige Perlen.</b><br>Zähle die Maschen und vergleiche sie mit dem Plan. Wenn etwas falsch ist, ziehe die Perlen Masche für Masche wieder ab, bis alles stimmt.</div>
    <div><b>Die Schnur ist zu kurz geworden.</b><br>Wenn ein Ende kürzer als deine Hand ist, holst du einen Erwachsenen. Er knotet ein neues Stück Schnur mit einem Doppelknoten an. Den Knoten versteckt ihr in einer Perle.</div>
    <div><b>Die Schnur passt nicht mehr durch die Perle.</b><br>Nicht mit Gewalt drücken! Schneide das Ende noch einmal schräg ab oder nimm die Pinzette zu Hilfe.</div>
    <div><b>Es ist eine flache Scheibe statt einer Kugel.</b><br>Das ist am Anfang ganz normal! Ab Runde 4 biegt sich der Rand nach oben. Drücke mit dem Daumen von innen nach.</div>
    <div><b>Mein Rind ist schlapp oder hat Dellen.</b><br>Da fehlt noch Watte! Stopfe mehr kleine Stücke hinein, vor allem unten in den Bauch. Mit der Pinzette kommst du gut in die Ecken.</div>
    <div><b>Alles ist wackelig.</b><br>Ziehe nach jeder Masche beide Enden fest. Du kannst auch am Ende einer Runde die Schnur noch einmal nachziehen.</div>
    <div><b>Die Farben sind „falsch herum“.</b><br>Keine Sorge: Blau und Rot tauschen nach jeder Masche die Seite. Wichtig ist nur: <b>untere</b> Schnur durch die alte Perle, <b>obere</b> Schnur nimmt die neuen.</div>
  </div>

  <div class="cert">
    <div class="cert-title">🏆 Geschafft! 🏆</div>
    {svg(420, 420, cow_body(seed=21), style="width:52mm;display:block;margin:0 auto")}
    <p>Mein Hochlandrind heißt: <span class="line"></span></p>
    <p>Fertig geworden am: <span class="line"></span></p>
    <p>Gefädelt von: <span class="line"></span></p>
  </div>
</div>''')

    html_doc = f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><title>Hochlandrind aus Perlen</title>
<style>{css}</style></head><body>{DEFS}{"".join(pages)}</body></html>'''
    out = Path(__file__).with_name('Hochlandrind-Anleitung.html')
    out.write_text(html_doc, encoding='utf-8')
    print('geschrieben:', out, '| Körperperlen:', total_body)


if __name__ == '__main__':
    build()
