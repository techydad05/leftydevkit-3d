#!/usr/bin/env python3
"""Replace THE SEAL with a big civic BALLOT BOX the camera flies into at the Arsenal section."""
HTML = r"C:\Users\techydad06\Projects\leftydevkit-3d\index.html"
html = open(HTML, encoding="utf-8").read()

# 1. replace makeSeal function with makeBallot
seal_fn_start = "// THE SEAL — volumetric civic medallion (ballot check), reads from any camera angle\nfunction makeSeal(){"
seal_fn_end = "  return g;\n}"
i0 = html.index(seal_fn_start)
i1 = html.index(seal_fn_end, i0) + len(seal_fn_end)
ballot_fn = '''// THE BALLOT BOX — a civic ballot drop the camera flies into (Arsenal)
function makeBallot(){
  const g = new THREE.Group();
  // the box body (volumetric, reads from any camera angle)
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.25, 1.6),
    new THREE.MeshBasicMaterial({ color: 0x2f7fd4, transparent: true, opacity: .85, side: THREE.DoubleSide }));
  g.add(body);
  // slot on the top lip where the ballot goes in
  const slot = new THREE.Mesh(new THREE.BoxGeometry(1.15, .06, .16),
    new THREE.MeshBasicMaterial({ color: 0x050a18, transparent: true, opacity: .95 }));
  slot.position.set(0, .73, .5); g.add(slot);
  // a ballot card angling in from the slot, with a BIG bold check
  const ballot = new THREE.Group();
  const card = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 1.55),
    new THREE.MeshBasicMaterial({ color: 0xe6f6ff, transparent: true, opacity: .94, side: THREE.DoubleSide }));
  ballot.add(card);
  const chk = new THREE.MeshBasicMaterial({ color: 0x0a1430, transparent: true, opacity: 1 });
  const c1 = new THREE.Mesh(new THREE.BoxGeometry(.95, .24, .03), chk); c1.position.set(-.3, -.18, .02); c1.rotation.z = .5;
  const c2 = new THREE.Mesh(new THREE.BoxGeometry(.24, 1.0, .03), chk); c2.position.set(.13, .3, .02); c2.rotation.z = -.58;
  ballot.add(c1, c2);
  ballot.position.set(0, .7, .6);
  g.add(ballot);
  // a civic seal sticker on the box face
  const sticker = new THREE.Mesh(new THREE.TorusGeometry(.5, .09, 10, 30),
    new THREE.MeshBasicMaterial({ color: 0x7dd3fc, transparent: true, opacity: .85 }));
  sticker.position.set(0, -.1, .81); g.add(sticker);
  const dot = new THREE.Mesh(new THREE.CircleGeometry(.16, 24),
    new THREE.MeshBasicMaterial({ color: 0x7dd3fc, transparent: true, opacity: .8 }));
  dot.position.set(0, -.1, .82); g.add(dot);
  return g;
}'''
html = html[:i0] + ballot_fn + html[i1:]

# 2. variable rename sealGrp -> ballotGrp
html = html.replace("const sealGrp = makeSeal(); scene.add(sealGrp);",
                    "const ballotGrp = makeBallot(); scene.add(ballotGrp);")
html = html.replace("setP(sealGrp, [-6.5, -1.5, -6]);", "setP(ballotGrp, [-6.5, -1.5, -6]);")
old_anim = """    // the seal (arsenal / join) — spins flat like a coin, facing the camera
    const sk = a.o.seal, st = b.o.seal;
    sealGrp.position.set(lerp(sk.p[0], st.p[0]), lerp(sk.p[1], st.p[1]), lerp(sk.p[2], st.p[2]));
    sealGrp.scale.setScalar(Math.max(.001, lerp(sk.s, st.s)));
    sealGrp.rotation.z += dt * .35;"""
new_anim = """    // the ballot box (arsenal) — gentle sway so the check stays facing you
    const sk = a.o.seal, st = b.o.seal;
    ballotGrp.position.set(lerp(sk.p[0], st.p[0]), lerp(sk.p[1], st.p[1]), lerp(sk.p[2], st.p[2]));
    ballotGrp.scale.setScalar(Math.max(.001, lerp(sk.s, st.s)));
    ballotGrp.rotation.y = Math.sin(t * .4) * .15;"""
assert old_anim in html
html = html.replace(old_anim, new_anim)

# 3. arsenal keyframe — camera flies INTO the ballot box
old_k3 = """  { p: 0.52, cam:{ p:[1.3,.85,5.2], l:[-6,-.6,-2.2] },              /* arsenal — seal peaks, parked near camera look target */
    o:{ fist:{p:[5.5,2,-5], s:.28}, cog:{p:[3,-2,-4], s:.3}, seal:{p:[-5.2,-.2,-1.6], s:1} } },"""
new_k3 = """  { p: 0.52, cam:{ p:[.8,1.0,3.6], l:[-1.2,.5,-.4] },               /* arsenal — fly INTO the ballot box */
    o:{ fist:{p:[5.5,2,-5], s:.28}, cog:{p:[3,-2,-4], s:.3}, seal:{p:[-1.5,.4,-.3], s:1.6} } },"""
assert old_k3 in html
html = html.replace(old_k3, new_k3)

open(HTML, "w", encoding="utf-8", newline="\n").write(html)
print("sealGrp left:", html.count("sealGrp"), "| makeBallot:", html.count("makeBallot"))
