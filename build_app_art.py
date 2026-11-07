#!/usr/bin/env python3
"""Erzeugt app/art.js: die Rind-Zeichnungen aus der PDF-Anleitung, in Ebenen zerlegt,
damit die App beim Zusammenbau Teil für Teil einblenden kann."""
import json
import math
import random
from pathlib import Path

from build_hochlandrind import BK, CR, D, H, M, bead, darker, hex_fill, quad

HAIR = [H, M, D]   # nur die drei Brauntöne aus der Anleitung


def cow_layers(seed=7):
    """Wie cow_body() in build_hochlandrind.py, aber jedes Teil als eigene Ebene (gleiche Zufallsfolge)."""
    rng = random.Random(seed)
    L = {}
    L['shadow'] = '<ellipse cx="200" cy="402" rx="150" ry="16" fill="#000" opacity=".10"/>'
    s = ''
    for i in range(10):
        x, y = quad((285, 330), (345, 330), (348, 262), i / 9)
        s += bead(x, y, 6.5, D)
    for a in (-60, -100, -140):
        for k in (1, 2, 3):
            s += bead(348 + math.cos(math.radians(a)) * 9 * k, 262 + math.sin(math.radians(a)) * 9 * k, 5.5, D)
    L['tail'] = s
    L['hindlegs'] = hex_fill(98, 372, 44, 22, [D, M], [3, 1], rng) + hex_fill(302, 372, 44, 22, [D, M], [3, 1], rng)
    L['body'] = hex_fill(200, 300, 112, 88, [M, D, H], [5, 3, 2], rng)
    L['frontlegs'] = hex_fill(156, 352, 26, 44, [D, M], [3, 1], rng) + hex_fill(244, 352, 26, 44, [D, M], [3, 1], rng)
    s = ''
    for side in (-1, 1):
        p0, p1, p2 = (200 + side * 62, 128), (200 + side * 150, 128), (200 + side * 140, 52)
        for i in range(13):
            t = i / 12
            x, y = quad(p0, p1, p2, t)
            s += bead(x, y, 11 - 6 * t, CR if i < 10 else '#E3CC9C')
    L['horns'] = s
    L['ears'] = hex_fill(92, 178, 42, 19, [M, H], [2, 1], rng, rot=18) + hex_fill(308, 178, 42, 19, [M, H], [2, 1], rng, rot=-18)
    L['head'] = hex_fill(200, 182, 96, 86, [M, D, H], [5, 3, 2], rng)
    L['eyes'] = ''.join(f'<circle cx="{ex}" cy="185" r="10" fill="{BK}"/><circle cx="{ex - 3}" cy="181" r="3.2" fill="#fff"/>'
                        for ex in (158, 242))
    s = ''
    for i, x0 in enumerate(range(116, 290, 13)):
        top = 182 - 86 * math.sqrt(max(0, 1 - ((x0 - 200) / 96) ** 2)) + 8
        n = 7 if abs(x0 - 200) < 50 else 5
        for k in range(n):
            x = x0 + math.sin(k * 0.9 + i) * 3 + (x0 - 200) * 0.04 * k
            y = top + k * 10.5
            if y > 168 and min(abs(x - 158), abs(x - 242)) < 20:
                break
            s += bead(x, y, 6.2, rng.choice(HAIR))
    L['hair'] = s
    L['mouth'] = hex_fill(200, 232, 58, 36, [CR, '#E8D3A8'], [4, 1], rng, r=6.2)
    L['nostrils'] = bead(181, 236, 8, BK) + bead(219, 236, 8, BK)
    return L


def fuellen():
    """Schnitt durch das Rind: Perlenhülle (oben offen) und Wattebäusche von unten nach oben."""
    def ring(cx, cy, rx, ry, n, skip):
        out = ''
        for i in range(n):
            a = 2 * math.pi * i / n - math.pi / 2
            if not skip(a):
                out += bead(cx + rx * math.cos(a), cy + ry * math.sin(a), 7, [H, M, D][i % 3])
        return out
    hull = ring(110, 135, 62, 44, 24, lambda a: math.sin(a) < -0.8)
    hull += ring(110, 70, 48, 40, 18, lambda a: math.sin(a) < -0.93 or math.sin(a) > 0.9)
    rng = random.Random(5)
    inside = lambda x, y: ((x - 110) / 52) ** 2 + ((y - 135) / 35) ** 2 < 1 or ((x - 110) / 39) ** 2 + ((y - 70) / 31) ** 2 < 1
    puffs = []
    for y in range(40, 175, 12):
        for x in range(56, 166, 13):
            px, py = x + rng.uniform(-4, 4), y + rng.uniform(-4, 4)
            if inside(px, py):
                puffs.append({'y': round(py, 1), 'svg': f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rng.uniform(8, 11):.1f}" '
                                                          f'fill="#fff" stroke="#ddd" stroke-width="1.5"/>'})
    puffs.sort(key=lambda p: -p['y'])
    return {'vb': [0, -10, 220, 200], 'hull': hull, 'puffs': puffs,
            'opening': [110, 30]}


def frisur():
    """Kopf von oben (wie frisur_top_svg): Grundbild, 10 Strähnen einzeln, Öffnung obenauf."""
    cx, cy, R = 150, 128, 100
    base = ''
    for ea in (10, 170):
        a = math.radians(ea)
        base += (f'<ellipse cx="{cx + (R + 14) * math.cos(a):.0f}" cy="{cy + (R + 14) * math.sin(a):.0f}" rx="22" ry="12" '
                 f'fill="{M}" stroke="{darker(M)}" stroke-width="2"/>')
    base += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#d9b48e" stroke="{darker("#d9b48e")}" stroke-width="2"/>'
    for ang in (-40, -140):
        a = math.radians(ang)
        for k in range(6):
            rr = R - 6 + k * 12
            base += bead(cx + rr * math.cos(a), cy + rr * math.sin(a), 8.5 - k * 0.7, CR)
    base += f'<ellipse cx="{cx}" cy="{cy + R + 4}" rx="44" ry="20" fill="{CR}" stroke="{darker(CR)}" stroke-width="2"/>'
    base += (f'<text x="{cx}" y="{cy + R + 44}" font-size="12.5" font-weight="700" fill="#5a2f14" text-anchor="middle">vorne = Gesicht ↓</text>'
             f'<text x="{cx}" y="12" font-size="12" font-weight="600" fill="#777" text-anchor="middle">hinten</text>')
    plan = [(a, 6) for a in (62, 81, 99, 118)] + [(a, 8) for a in (150, 205, 30, -25, 245, 295)]
    strands = []
    for i, (ang, n) in enumerate(plan):
        a = math.radians(ang)
        cols = [H, M, H, H] if i % 2 == 0 else [D, M, D, D]
        s = (f'<line x1="{cx + 14 * math.cos(a):.0f}" y1="{cy + 14 * math.sin(a):.0f}" '
             f'x2="{cx + (20 + (n - 1) * 11) * math.cos(a):.0f}" y2="{cy + (20 + (n - 1) * 11) * math.sin(a):.0f}" '
             f'stroke="#8B5A2B" stroke-width="3"/>')
        for k in range(n):
            rr = 22 + k * 11
            s += bead(cx + rr * math.cos(a), cy + rr * math.sin(a), 5.6, cols[k % 4])
        strands.append(s)
    opening = ''.join(bead(cx + 11 * math.cos(math.radians(k * 60)), cy + 11 * math.sin(math.radians(k * 60)), 5.5, D)
                      for k in range(6))
    return {'vb': [0, 0, 300, 290], 'center': [cx, cy], 'base': base, 'strands': strands, 'opening': opening}


def main():
    art = {
        'cow': {'vb': [20, 20, 380, 400], 'layers': cow_layers()},
        'fuellen': fuellen(),
        'frisur': frisur(),
    }
    out = Path(__file__).parent / 'app' / 'art.js'
    out.write_text('// Erzeugt von build_app_art.py – nicht von Hand ändern.\nwindow.ART = '
                   + json.dumps(art, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    print('geschrieben:', out, f'({out.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
