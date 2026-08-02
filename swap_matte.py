#!/usr/bin/env python3
"""Pivot the 3D scene from neon-glow to a matte studio/blueprint look with civic objects."""
HTML = r"C:\Users\techydad06\Projects\leftydevkit-3d\index.html"
html = open(HTML, encoding="utf-8").read()

# ---------- A) Replace stars..K block with matte build ----------
a_start = html.index("/* stars — two layers */")
a_end = html.index("/* post-processing bloom */")

new_build = r'''/* stars — faint matte backdrop speckle */
function starLayer(count, size, color, rMin, rMax, opacity){
  const g = new THREE.BufferGeometry();
  const p = new Float32Array(count * 3);
  for(let i = 0; i < count; i++){
    const r = rMin + Math.random() * (rMax - rMin);
    const th = Math.random() * Math.PI * 2, ph = Math.acos(2 * Math.random() - 1);
    p[i*3]   = r * Math.sin(ph) * Math.cos(th);
    p[i*3+1] = r * Math.sin(ph) * Math.sin(th);
    p[i*3+2] = r * Math.cos(ph);
  }
  g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  return new THREE.Points(g, new THREE.PointsMaterial({ color, size, sizeAttenuation: true, transparent: true, opacity }));
}
const starsFar  = starLayer(isMobile ? 500 : 900, .32, 0x9aa7bd, 45, 90, .35);
const starsNear = starLayer(isMobile ? 250 : 500, .45, 0xc9d6e8, 30, 60, .3);
scene.add(starsFar, starsNear);

/* ── LIGHTING — matte studio scenes, not neon glow ── */
scene.add(new THREE.AmbientLight(0x9fb4d8, .65));
const keyLight = new THREE.DirectionalLight(0xdfeaff, 1.15); keyLight.position.set(5, 7, 6);
scene.add(keyLight);
const rimLight = new THREE.DirectionalLight(0x7cc4ff, .55); rimLight.position.set(-5, 3, -5);
scene.add(rimLight);
const fillLight = new THREE.DirectionalLight(0x2c3a54, .45); fillLight.position.set(-3, -2, 4);
scene.add(fillLight);

/* ── materials (matte) ── */
const M_STONE = new THREE.MeshStandardMaterial({ color: 0x9db2d4, roughness: .85, metalness: .05 });
const M_DEEP  = new THREE.MeshStandardMaterial({ color: 0x3f6ba8, roughness: .6,  metalness: .15 });
const M_IRON  = new THREE.MeshStandardMaterial({ color: 0x38506e, roughness: .5,  metalness: .55 });
const M_LITE  = new THREE.MeshStandardMaterial({ color: 0xdcebfa, roughness: .35, metalness: .3 });
const M_DARK  = new THREE.MeshStandardMaterial({ color: 0x101b2e, roughness: .7,  metalness: .2 });

/* THE PEOPLE'S FIST — solid voxel bricks (matte; ties to the boot's brick fist) */
const VOX = [
  '....XX......','...XXXXX....','..XXXXXXX...','..XXXXXXXX..','.XXXXXXXXXX.',
  'XXXX.XXXXXXX','XXXXX.XXXXXX','XXXXXXXXXXXX','.XXXXXXXXXXX','..XXXXXXXXX.',
  '...XXXXXXXX.','...XXXXXXX..','...XXXXXXX..','...XXXXXXX..','...XXXXXXX..',
  '...XXXXXXX..','...XXXXXXX..','...XXXXXXX..','...XXXXXXX..','..XXXXXXXX..',
  '..XXXXXXXX..'
];
function buildVoxelFist(){
  const g = new THREE.Group();
  const cell = 4.2 / VOX.length;
  const w = VOX[0].length;
  VOX.forEach((row, ry) => {
    for (let cx = 0; cx < w; cx++){
      if (row[cx] !== 'X') continue;
      const b = new THREE.Mesh(new THREE.BoxGeometry(cell * .94, cell * .94, cell * .94), M_DEEP);
      const depth = ((cx + ry) % 2) ? cell * .26 : 0;      // staggered brick depth
      b.position.set((cx - w / 2) * cell, -(ry - VOX.length / 2) * cell, depth);
      g.add(b);
    }
  });
  return g;
}
const fistGrp = buildVoxelFist(); scene.add(fistGrp);

/* THE COG — matte steel gear */
function makeCog(){
  const g = new THREE.Group();
  g.add(new THREE.Mesh(new THREE.TorusGeometry(1.05, .3, 8, 28), M_IRON));
  for (let i = 0; i < 8; i++){
    const a = (i / 8) * Math.PI * 2;
    const t = new THREE.Mesh(new THREE.BoxGeometry(.5, .5, .34), M_LITE);
    t.position.set(Math.cos(a) * 1.3, Math.sin(a) * 1.3, 0);
    t.rotation.z = a;
    g.add(t);
  }
  g.add(new THREE.Mesh(new THREE.TorusGeometry(.4, .16, 8, 20), M_DARK));
  return g;
}
const cogGrp = makeCog(); scene.add(cogGrp);

/* THE COURTHOUSE — matte civic building (the system we reclaim) */
function makeBuilding(){
  const g = new THREE.Group();
  const step1 = new THREE.Mesh(new THREE.BoxGeometry(3.6, .35, 2.6), M_STONE); step1.position.y = .18;
  const step2 = new THREE.Mesh(new THREE.BoxGeometry(3.0, .35, 2.2), M_STONE); step2.position.y = .52;
  g.add(step1, step2);
  const base = new THREE.Mesh(new THREE.BoxGeometry(2.5, .5, 1.8), M_STONE); base.position.y = .95;
  g.add(base);
  const colGeo = new THREE.CylinderGeometry(.17, .2, 1.6, 12);
  for (let i = 0; i < 4; i++){
    const col = new THREE.Mesh(colGeo, M_STONE);
    col.position.set(-.9 + i * .6, 2.0, 0);
    g.add(col);
  }
  const beam = new THREE.Mesh(new THREE.BoxGeometry(2.9, .3, 2.0), M_STONE); beam.position.y = 2.9;
  g.add(beam);
  const ped = new THREE.Mesh(new THREE.ConeGeometry(1.45, .7, 3), M_DEEP);
  ped.position.y = 3.4; ped.rotation.y = Math.PI / 3;
  g.add(ped);
  return g;
}
const buildingGrp = makeBuilding(); buildingGrp.rotation.y = Math.PI * .12; scene.add(buildingGrp);

/* THE LAPTOP — matte rig with a lit code screen (built in public) */
function makeLaptop(){
  const g = new THREE.Group();
  const metal = new THREE.MeshStandardMaterial({ color: 0x2a3a52, roughness: .4, metalness: .6 });
  const base = new THREE.Mesh(new THREE.BoxGeometry(1.9, .1, 1.2), metal);
  base.position.y = -.05; g.add(base);
  const screen = new THREE.Group(); screen.position.set(0, .05, -.46); screen.rotation.x = -.34;
  const frame = new THREE.Mesh(new THREE.BoxGeometry(1.75, 1.15, .06), metal);
  frame.position.y = .55; screen.add(frame);
  const disp = new THREE.Mesh(new THREE.PlaneGeometry(1.55, .98),
    new THREE.MeshStandardMaterial({ color: 0x0b1420, emissive: 0x6fb7ff, emissiveIntensity: .9, side: THREE.DoubleSide }));
  disp.position.set(0, .55, .045); screen.add(disp);
  const bar = new THREE.Mesh(new THREE.BoxGeometry(.34, .05, .01),
    new THREE.MeshBasicMaterial({ color: 0xeaf6ff }));
  bar.position.set(-.12, .4, .052); screen.add(bar);
  g.add(screen);
  return g;
}
const laptopGrp = makeLaptop(); scene.add(laptopGrp);

/* ── SCROLL TIMELINE — camera + object keyframes aligned to section scroll positions ── */
const K = [
  { p:0.00, cam:{ p:[0,.5,7.5], l:[0,1.2,0] },                     /* hero — the fist */
    o:{ fist:{p:[2.9,.6,0],s:1}, cog:{p:[-6,-1,-5],s:.001}, bld:{p:[-7,-1.5,-6],s:.001}, lap:{p:[-7,1,-6],s:.001} } },
  { p:0.16, cam:{ p:[2.0,.8,6.4], l:[-1.5,.2,-1] },                /* mission — cog arrives */
    o:{ fist:{p:[6,-1,-4],s:.38}, cog:{p:[-1.3,.3,0],s:1.0}, bld:{p:[-7,-1.5,-6],s:.001}, lap:{p:[-6.5,1,-6],s:.001} } },
  { p:0.35, cam:{ p:[.3,.7,5.0], l:[0,1.6,0] },                    /* stack — cog */
    o:{ fist:{p:[5,-2,-5],s:.26}, cog:{p:[0,1.4,0],s:1.4}, bld:{p:[-6.5,-.5,-5],s:.001}, lap:{p:[5.5,2,-5],s:.001} } },
  { p:0.52, cam:{ p:[.4,.9,3.9], l:[0,2.1,-1] },                   /* arsenal — fly into the courthouse */
    o:{ fist:{p:[5.5,-2,-5],s:.26}, cog:{p:[3.5,-1.5,-3],s:.25}, bld:{p:[0,1.05,-.6],s:1.45}, lap:{p:[-6,1,-5],s:.001} } },
  { p:0.74, cam:{ p:[.5,1.0,3.6], l:[-1.9,.95,-.3] },              /* manifesto — fly into the laptop */
    o:{ fist:{p:[5,2,-4],s:.3}, cog:{p:[5,-2,-4],s:.25}, bld:{p:[5.5,-1.5,-5],s:.3}, lap:{p:[-1.7,.95,-.3],s:1.5} } },
  { p:1.00, cam:{ p:[0,1.4,8.0], l:[0,1.2,0] },                    /* join — all spread */
    o:{ fist:{p:[2.6,.4,1.5],s:.7}, cog:{p:[-4,-.5,-2],s:.45}, bld:{p:[4,-.6,-1.5],s:.5}, lap:{p:[-3,1.4,-.5],s:.5} } },
];

'''
html = html[:a_start] + new_build + html[a_end:]

# ---------- B) kill the bloom glow ----------
old_bloom = "const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), .72, .55, .05);"
new_bloom = "const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), .06, .5, .0);"
assert old_bloom in html
html = html.replace(old_bloom, new_bloom)

# ---------- C) rewrite the animate scroll-flythrough block ----------
c_start = html.index("  /* ── FIRESHIP-STYLE SCROLL FLYTHROUGH ──")
c_end = html.index("  starsFar.rotation.y -= dt * .004 * spin;") + len("  starsFar.rotation.y -= dt * .004 * spin;")

new_anim = r'''  /* ── SCROLL FLYTHROUGH — camera + the four matte civic objects ride a keyframe timeline ── */
  function setP(g, v, s){ g.position.set(v[0], v[1], v[2]); g.scale.setScalar(s || .001); }

  if (reduced){
    camera.position.set(0, .5, 7.5); camera.lookAt(0, 1.2, 0);
    fistGrp.position.set(2.9, .6, 0); fistGrp.rotation.y = 0; fistGrp.scale.setScalar(1);
    setP(cogGrp, [-6, -1, -5]); setP(buildingGrp, [-7, -1.5, -6]); setP(laptopGrp, [-7, 1, -6]);
  } else {
    const p = scrollP;
    let ki = 0;
    for (let i = 0; i < K.length - 1; i++) if (p >= K[i].p) ki = i;
    const a = K[ki], b = K[ki + 1];
    const f = Math.min(1, Math.max(0, (p - a.p) / (b.p - a.p)));
    const s = f * f * (3 - 2 * f); // smoothstep
    const lerp = (u, v) => u + (v - u) * s;
    const lerpV = (u, v) => [ lerp(u[0], v[0]), lerp(u[1], v[1]), lerp(u[2], v[2]) ];

    // camera (plus a whisper of mouse parallax)
    const cp = lerpV(a.cam.p, b.cam.p), cl = lerpV(a.cam.l, b.cam.l);
    camera.position.set(cp[0] + mouse.x * .3, cp[1] - mouse.y * .2, cp[2]);
    camera.lookAt(cl[0], cl[1], cl[2]);

    // the fists (hero / manifesto) — gentle sway, never edge-on
    const fk = a.o.fist, ft = b.o.fist;
    fistGrp.position.set(lerp(fk.p[0], ft.p[0]), lerp(fk.p[1], ft.p[1]), lerp(fk.p[2], ft.p[2]));
    fistGrp.rotation.y = Math.sin(t * .22) * .5;
    fistGrp.scale.setScalar(lerp(fk.s, ft.s));

    // the cog (machine / stack) — turns in place
    const ck = a.o.cog, ct = b.o.cog;
    cogGrp.position.set(lerp(ck.p[0], ct.p[0]), lerp(ck.p[1], ct.p[1]), lerp(ck.p[2], ct.p[2]));
    cogGrp.scale.setScalar(Math.max(.001, lerp(ck.s, ct.s)));
    cogGrp.rotation.z += dt * .5;

    // the courthouse — slow float
    const bk = a.o.bld, bt = b.o.bld;
    buildingGrp.position.set(lerp(bk.p[0], bt.p[0]), lerp(bk.p[1], bt.p[1]) + Math.sin(t * .4) * .06, lerp(bk.p[2], bt.p[2]));
    buildingGrp.scale.setScalar(Math.max(.001, lerp(bk.s, bt.s)));
    buildingGrp.rotation.y = Math.PI * .12 + Math.sin(t * .12) * .04;

    // the laptop — gentle sway, lit screen toward camera
    const lk = a.o.lap, lt = b.o.lap;
    laptopGrp.position.set(lerp(lk.p[0], lt.p[0]), lerp(lk.p[1], lt.p[1]), lerp(lk.p[2], lt.p[2]));
    laptopGrp.scale.setScalar(Math.max(.001, lerp(lk.s, lt.s)));
    laptopGrp.rotation.y = Math.sin(t * .3) * .14;
  }

  // faint star drift
  starsNear.rotation.y += dt * .006;
  starsFar.rotation.y -= dt * .003;
'''
html = html[:c_start] + new_anim + html[c_end:]

open(HTML, "w", encoding="utf-8", newline="\n").write(html)
# sanity checks
for token in ["halo.scale", "orbitA.", "core.position", "ballotGrp", "sealGrp"]:
    print(token, "->", html.count(token))
print("fistGrp:", html.count("fistGrp"), "| buildingGrp:", html.count("buildingGrp"), "| laptopGrp:", html.count("laptopGrp"))
