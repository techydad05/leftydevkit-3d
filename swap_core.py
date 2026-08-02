#!/usr/bin/env python3
"""Swap the abstract 3D core for a particle raised fist (built from the logo mask)."""
import re

HTML = r"C:\Users\techydad06\Projects\leftydevkit-3d\index.html"
MASK = r"C:\Users\techydad06\Projects\leftydevkit-3d\fist-mask-hi.txt"

rows = open(MASK).read().strip().split("\n")
# build the JS array literal
arr = "[\n" + ",\n".join("  '" + r + "'" for r in rows) + "\n]"

new_block = f"""/* the PEOPLE'S FIST — a raised fist of particles, built from the logo mask */
const FIST_HI = {arr};
function buildFistPoints(countPerCell){{
  const positions = [], colors = [];
  const cell = 5.6 / FIST_HI.length;           // fist stands ~5.6 units tall
  const w = FIST_HI[0].length;
  const h = FIST_HI.length;
  const cA = new THREE.Color(0x3ba6f2), cB = new THREE.Color(0x7dd3fc);
  const tmp = new THREE.Color();
  for(let ry = 0; ry < h; ry++){{
    const row = FIST_HI[ry];
    for(let cx = 0; cx < w; cx++){{
      if(row[cx] !== 'X') continue;
      for(let k = 0; k < countPerCell; k++){{
        const x = (cx - w/2 + (Math.random() - .5) * .7) * cell;
        const y = -(ry - h/2 + (Math.random() - .5) * .7) * cell;
        const z = (Math.random() - .5) * cell * 2.6;
        positions.push(x, y, z);
        tmp.copy(cA).lerp(cB, Math.random() * .8 + .1);
        colors.push(tmp.r, tmp.g, tmp.b);
      }}
    }}
  }}
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  return g;
}}
const core = new THREE.Group();
const halo = new THREE.Mesh(
  new THREE.SphereGeometry(1.9, 32, 32),
  new THREE.MeshBasicMaterial({{ color: 0x3ba6f2, transparent: true, opacity: .1, side: THREE.BackSide }})
);
const heart = new THREE.Mesh(
  new THREE.SphereGeometry(.62, 24, 24),
  new THREE.MeshBasicMaterial({{ color: 0x7dd3fc, transparent: true, opacity: .85 }})
);
const fist = new THREE.Points(
  buildFistPoints(isMobile ? 3 : 5),
  new THREE.PointsMaterial({{ size: isMobile ? .09 : .075, sizeAttenuation: true, vertexColors: true, transparent: true, opacity: .96 }})
);
core.add(halo, heart, fist);

/* gyroscope rings */
function ring(radius, tube, color, opacity, rx, ry){{
  const m = new THREE.Mesh(
    new THREE.TorusGeometry(radius, tube, 12, 90),
    new THREE.MeshBasicMaterial({{ color, transparent: true, opacity }})
  );
  m.rotation.x = rx; m.rotation.y = ry;
  core.add(m);
  return m;
}}
const rings = [
  ring(4.2, .016, 0x3ba6f2, .55, Math.PI/2.4, 0),
  ring(4.9, .011, 0x7cfc98, .32, Math.PI/1.9, Math.PI/4),
  ring(5.6, .008, 0xf2f0ec, .18, Math.PI/3.1, -Math.PI/3),
];

/* orbiting community particles */
function orbitRing(count, radius, color, size){{
  const g = new THREE.BufferGeometry();
  const p = new Float32Array(count * 3);
  for(let i = 0; i < count; i++){{
    const a = (i / count) * Math.PI * 2;
    const j = (Math.random() - .5) * .06;
    p[i*3] = Math.cos(a) * radius; p[i*3+1] = j * radius; p[i*3+2] = Math.sin(a) * radius;
  }}
  g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({{ color, size, sizeAttenuation: true, transparent: true, opacity: .9 }}));
  core.add(pts);
  return pts;
}}
const orbitA = orbitRing(isMobile ? 120 : 240, 4.6, 0x7dd3fc, .06);
const orbitB = orbitRing(isMobile ? 90 : 180, 5.3, 0x7cfc98, .045);

core.position.x = isMobile ? 0 : 2.7;
core.position.y = 0;
scene.add(core);"""

html = open(HTML, encoding="utf-8").read()
start = html.index("/* the SIGNAL CORE */")
end = html.index("scene.add(core);") + len("scene.add(core);")
html = html[:start] + new_block + html[end:]
open(HTML, "w", encoding="utf-8", newline="\n").write(html)
print("replaced block, new length:", len(html))
