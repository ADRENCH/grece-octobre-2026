# Génère maps.html : la carte bureau (une seule vue) et deux cartes recadrées pour téléphone.
import json, math

t = json.load(open('data/countries-10m.json'))
sc, tr = t['transform']['scale'], t['transform']['translate']
arcs = []
for a in t['arcs']:
    x = y = 0
    pts = []
    for dx, dy in a:
        x += dx; y += dy
        pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
    arcs.append(pts)

def arc(i):
    return arcs[i] if i >= 0 else arcs[~i][::-1]

rings = []
for g in t['objects']['countries']['geometries']:
    if g.get('properties', {}).get('name') not in ('Greece', 'Turkey'):
        continue
    polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
    for poly in polys:
        for ring in poly:
            pts = []
            for i in ring:
                a = arc(i)
                pts.extend(a if not pts else a[1:])
            rings.append(pts)

K = math.cos(math.radians(37.75))
ATH = (23.947, 37.936); ATHC = (23.730, 37.985); CANAL = (22.985, 37.93); ACRO = (22.870, 37.890)
MYC = (22.756, 37.731); NEMEA = (22.711, 37.809); NAF = (22.802, 37.567); V1 = (22.8665, 37.5594)
EPID = (23.079, 37.596); RAF = (24.009, 38.022); MYK = (25.3164, 37.4852); PORT = (25.325, 37.458)
DELOS = (25.268, 37.397); HOUSE = (23.9003, 37.8873); SOUN = (24.025, 37.650); ACROP = (23.7257, 37.9715)

ROUTES = [
    ('r pelo', [ATH, (23.80, 38.03), (23.55, 38.04), (23.35, 37.99), CANAL, (22.86, 37.82), (22.76, 37.66), NAF, V1]),
    ('r pelo', [V1, (22.76, 37.66), MYC, NEMEA, ACRO, CANAL]),
    ('r pelo', [V1, (22.98, 37.60), EPID]),
    ('r pelo', [V1, (22.76, 37.66), (22.86, 37.82), CANAL, (23.35, 37.99), (23.55, 38.04), (23.80, 38.05), RAF]),
    ('f', [RAF, (24.30, 37.97), (24.62, 37.80), (25.00, 37.55), (25.22, 37.50), PORT]),
    ('f small', [PORT, (25.30, 37.42), DELOS]),
    ('r att', [RAF, (23.95, 37.95), HOUSE]),
    ('r att', [HOUSE, (23.97, 37.75), SOUN]),
    ('m', [HOUSE, (23.85, 37.94), (23.78, 37.98), ATHC]),
    ('r att', [HOUSE, ATH]),
]


def build(cls, lon0, lon1, lat0, lat1, s, sights, bases, texts, title, sr=4, br=11, scale_left=False):
    W = (lon1 - lon0) * K * s
    H = (lat1 - lat0) * s
    P = lambda lon, lat: ((lon - lon0) * K * s, (lat1 - lat) * s)

    def path(pts):
        xy = [P(*p) for p in pts]
        d = f'M{xy[0][0]:.1f},{xy[0][1]:.1f}'
        for i in range(len(xy) - 1):
            p0 = xy[i - 1] if i > 0 else xy[i]
            p1, p2 = xy[i], xy[i + 1]
            p3 = xy[i + 2] if i + 2 < len(xy) else xy[i + 1]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
        return d

    land = []
    for pts in rings:
        if not any(lon0 - .4 < x < lon1 + .4 and lat0 - .4 < y < lat1 + .4 for x, y in pts):
            continue
        xy = [P(x, y) for x, y in pts]
        out = [xy[0]]
        for q in xy[1:]:
            if abs(q[0] - out[-1][0]) + abs(q[1] - out[-1][1]) > 0.6:
                out.append(q)
        if len(out) >= 3:
            land.append('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in out) + 'Z')

    o = [f'<svg class="map {cls}" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{title}">',
         f'<rect width="{W:.0f}" height="{H:.0f}" fill="var(--sea)"/>',
         f'<path d="{" ".join(land)}" fill="var(--land)" stroke="var(--coast)" stroke-width=".8" stroke-linejoin="round"/>']
    for c, pts in ROUTES:
        o.append(f'<path class="{c}" d="{path(pts)}"/>')
    for (lon, lat), txt, c in texts:
        x, y = P(lon, lat)
        o.append(f'<text class="{c}" x="{x:.1f}" y="{y:.1f}">{txt}</text>')
    for p, label, dx, dy, anchor in sights:
        x, y = P(*p)
        o.append(f'<circle class="s" cx="{x:.1f}" cy="{y:.1f}" r="{sr}"/>')
        o.append(f'<text class="sl" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{label}</text>')
    for p, n, label, date, dx, dy, anchor, c in bases:
        x, y = P(*p)
        o.append(f'<g class="b {c}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{br}"/>'
                 f'<text class="bn" x="{x:.1f}" y="{y:.1f}" dy=".36em" text-anchor="middle">{n}</text>'
                 f'<text class="bl" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{label}</text>'
                 f'<text class="bd" x="{x + dx:.1f}" y="{y + dy:.1f}" dy="1.3em" text-anchor="{anchor}">{date}</text></g>')
    px = 50 / 111.32 * s
    x0, y0 = (24 if scale_left else W - px - 24), H - 18
    o.append(f'<g class="scale"><path d="M{x0:.1f},{y0:.1f} h{px:.1f} M{x0:.1f},{y0 - 4:.1f} v8 M{x0 + px:.1f},{y0 - 4:.1f} v8"/>'
             f'<text x="{x0 + px / 2:.1f}" y="{y0 - 8:.1f}" text-anchor="middle">50 km</text></g>')
    o.append('</svg>')
    return '\n'.join(o)


ISL = [((24.80, 37.93), 'Andros', 'isl'), ((25.12, 37.62), 'Tinos', 'isl'), ((24.86, 37.43), 'Syros', 'isl')]

desk = build('desk', 22.45, 25.6, 37.22, 38.24, 401.5,
    [(CANAL, 'Canal de Corinthe', 9, -9, 'start'), (ACRO, 'Acrocorinthe', -9, 4, 'end'), (MYC, 'Mycènes', -9, 4, 'end'),
     (NEMEA, 'Némée', -9, 4, 'end'), (EPID, 'Épidaure', 9, 4, 'start'), (DELOS, 'Délos', -9, 4, 'end'),
     (SOUN, 'Cap Sounion', 9, 5, 'start'), (ACROP, 'Acropole', -9, 13, 'end'), (ATH, 'Aéroport', 9, 4, 'start'),
     (RAF, 'Rafina', 9, -6, 'start'), (PORT, 'Chora', 9, 7, 'start')],
    [(ATHC, '1', 'Athènes', 'sam. 3', -14, -16, 'end', 'att'), (V1, '2', 'Lefkakia · Nauplie', '4 → 7', 15, 24, 'start', 'pelo'),
     (MYK, '3', 'Villa Mykonos', '7 → 8', -15, -16, 'end', 'cyc'), (HOUSE, '4', 'Maison Petrino', '8 → 11', 15, 24, 'start', 'att')],
    [((22.52, 37.30), 'PÉLOPONNÈSE', 'rg'), ((23.80, 38.19), 'ATTIQUE', 'rg'), ((25.05, 38.15), 'CYCLADES', 'rg'),
     ((23.30, 37.70), 'Golfe Saronique', 'sea-l'), ((24.40, 37.55), 'Mer Égée', 'sea-l'), ((24.42, 37.92), '≈ 2 h 40 de ferry', 'fl')] + ISL,
    'Carte du parcours : Athènes, Péloponnèse, Mykonos, Attique')

mob_a = build('mob', 22.55, 24.22, 37.44, 38.12, 483.4,
    [(CANAL, 'Canal de Corinthe', 9, -8, 'start'), (ACRO, 'Acrocorinthe', 9, 12, 'start'), (NEMEA, 'Némée', 9, 7, 'start'),
     (MYC, 'Mycènes', 9, 7, 'start'), (EPID, 'Épidaure', 9, 7, 'start'), (SOUN, 'Cap Sounion', -10, 7, 'end'),
     (ATH, 'Aéroport', 9, 4, 'start'), (RAF, 'Rafina', 9, -4, 'start')],
    [(ATHC, '1', 'Athènes', 'sam. 3', -17, -14, 'end', 'att'), (V1, '2', 'Lefkakia · Nauplie', '4 → 7', 17, 20, 'start', 'pelo'),
     (HOUSE, '4', 'Maison Petrino', '8 → 11', -17, 22, 'end', 'att')],
    [((22.58, 38.08), 'PÉLOPONNÈSE', 'rg'), ((23.80, 38.10), 'ATTIQUE', 'rg'), ((23.25, 37.72), 'Golfe Saronique', 'sea-l')],
    'Carte : Péloponnèse et Attique', sr=5, br=13)

mob_b = build('mob', 23.95, 25.55, 37.30, 38.10, 483.4,
    [(RAF, 'Rafina', 9, -6, 'start'), (DELOS, 'Délos', 10, 8, 'start'), (PORT, 'Chora', 10, 9, 'start')],
    [(MYK, '3', 'Villa Mykonos', '7 → 8', -17, 34, 'end', 'cyc')],
    [((25.20, 38.06), 'CYCLADES', 'rg'), ((24.30, 37.62), 'Mer Égée', 'sea-l'), ((24.20, 37.86), '≈ 2 h 40 de ferry', 'fl'),
     ((24.80, 37.93), 'Andros', 'isl'), ((25.12, 37.62), 'Tinos', 'isl'), ((24.74, 37.40), 'Syros', 'isl')],
    'Carte : la traversée vers Mykonos', sr=5, br=13, scale_left=True)

with open('maps.html', 'w', encoding='utf-8') as f:
    f.write(desk + '\n<div class="mob-maps">\n<p class="mob-cap">Péloponnèse et Attique</p>\n' + mob_a +
            '\n<p class="mob-cap">La traversée vers Mykonos</p>\n' + mob_b + '\n</div>')
print('maps ok')
