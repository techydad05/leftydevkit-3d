#!/usr/bin/env python3
"""Replace the DOM brick-grid boot with the canvas 'Fist Forge' (blueprint -> bricks)."""
import re

HTML = r"C:\Users\techydad06\Projects\leftydevkit-3d\index.html"
MASK = r"C:\Users\techydad06\Projects\leftydevkit-3d\fist-mask-boot.txt"

rows = open(MASK).read().strip().split("\n")
mask_arr = "[\n" + ",\n".join("    '" + r + "'" for r in rows) + "\n  ]"

new_block = '''  /* ── BOOT OVERLAY — the FIST FORGE: a blueprint schematic that fills with bricks, becomes real ── */
  const boot = $('#boot'), bootCanvas = $('#bootCanvas'), bootBar = $('#bootBar'),
        bootFist = $('#bootFist'), bootWord = $('#bootWord');
  function showRealLogo(){
    bootCanvas.classList.add('fade');          // bricks dissolve as the real fist takes over
    bootFist.classList.add('show');            // fist becomes real (overlay on bricks)
    setTimeout(() => bootWord.classList.add('show'), 260); // then wordmark completes it
  }
  const BOOT_MASK = __MASK__;
  let bootDone = false;
  // dev hook: ?boothold keeps the built fist on screen until you click
  const BOOT_HOLD = new URLSearchParams(location.search).has('boothold');
  const bootStart = performance.now();
  function dismissBoot(){
    // in hold mode, ignore stray input events for the first 5s
    if (BOOT_HOLD && performance.now() - bootStart < 5000) return;
    finishBoot('dismiss:' + (performance.now() - bootStart).toFixed(0) + 'ms');
  }
  function finishBoot(why){
    if (bootDone) return; bootDone = true;
    window.__bootLog = window.__bootLog || [];
    window.__bootLog.push(why || 'finish:' + (performance.now() - bootStart).toFixed(0) + 'ms hold=' + BOOT_HOLD);
    boot.classList.add('done');
    setTimeout(() => boot.remove(), 650);
  }
  const GRID_W = BOOT_MASK[0].length, GRID_H = BOOT_MASK.length;
  function isEdge(cx, ry){
    for (const d of [[1,0],[-1,0],[0,1],[0,-1]]){
      const nx = cx + d[0], ny = ry + d[1];
      if (nx < 0 || ny < 0 || nx >= GRID_W || ny >= GRID_H) return true;
      if (BOOT_MASK[ny][nx] !== 'X') return true;
    }
    return false;
  }
  const BRICKS = [];
  for (let ry = 0; ry < GRID_H; ry++){
    const row = BOOT_MASK[ry];
    for (let cx = 0; cx < GRID_W; cx++){
      if (row[cx] !== 'X') continue;
      BRICKS.push({ cx, ry, edge: isEdge(cx, ry), shade: (cx + ry) % 2 });
    }
  }
  const easeOut = t => 1 - Math.pow(1 - t, 3);
  const clampV = (v, a, b) => Math.max(a, Math.min(b, v));
  function rrect(ctx, x, y, w, h, r){
    r = Math.max(0, Math.min(r, w / 2, h / 2));
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  function buildFist(){
    const dpr = Math.min(devicePixelRatio || 1, 2);
    const targetH = Math.min(innerHeight * 0.5, 520);
    const cell = targetH / GRID_H;
    const cssW = GRID_W * cell, cssH = GRID_H * cell;
    bootCanvas.width = Math.round(cssW * dpr);
    bootCanvas.height = Math.round(cssH * dpr);
    bootCanvas.style.width = cssW + 'px';
    bootCanvas.style.height = cssH + 'px';
    const ctx = bootCanvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // offscreen STATIC layer: grid + every settled brick drawn once, blitted each frame
    const st = document.createElement('canvas');
    st.width = bootCanvas.width; st.height = bootCanvas.height;
    const sctx = st.getContext('2d');
    sctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    sctx.strokeStyle = 'rgba(125,211,252,.05)'; sctx.lineWidth = 1;
    for (let gx = 0; gx <= GRID_W; gx += 6){ sctx.beginPath(); sctx.moveTo(gx * cell, 0); sctx.lineTo(gx * cell, cssH); sctx.stroke(); }
    for (let gy = 0; gy <= GRID_H; gy += 6){ sctx.beginPath(); sctx.moveTo(0, gy * cell); sctx.lineTo(cssW, gy * cell); sctx.stroke(); }
    const t0 = performance.now();
    const SETTLE = 170;
    const settled = new Set();
    function drawBrick(tctx, b, alpha, scale){
      const s = cell, m = s * 0.1, w = s - m, h = s - m;
      const x0 = b.cx * s, y0 = b.ry * s;
      const sc = clampV(scale, 0.01, 1), sw = w * sc, sh = h * sc;
      const x = x0 + (w - sw) / 2, y = y0 + (h - sh) + (1 - sc) * s * .3;
      tctx.globalAlpha = alpha;
      tctx.fillStyle = b.shade ? 'rgb(48,120,196)' : 'rgb(61,143,220)';
      rrect(tctx, x, y, sw, sh, Math.max(1, s * 0.14));
      tctx.fill();
      tctx.fillStyle = 'rgba(150,220,255,.28)';
      rrect(tctx, x, y, sw, Math.max(1.5, sh * 0.16), 1);
      tctx.fill();
      tctx.globalAlpha = 1;
    }
    function tick(){
      const t = performance.now() - t0;
      ctx.clearRect(0, 0, cssW, cssH);
      ctx.drawImage(st, 0, 0);
      if (t < 900){
        const bp = clampV(t / 550, 0, 1);
        ctx.save(); ctx.shadowColor = 'rgba(125,211,252,.9)'; ctx.shadowBlur = 6;
        for (const b of BRICKS){ if (b.edge) drawBrick(ctx, b, Math.min(1, bp * 1.6), 1); }
        ctx.restore();
      }
      if (t > 550){
        for (const b of BRICKS){
          const placeT = 550 + ((GRID_H - 1 - b.ry) / GRID_H) * 1550 + (b.cx % 7) * 14;
          const since = t - placeT;
          if (since < 0) continue;
          if (settled.has(b)) continue;
          if (since >= SETTLE){ drawBrick(sctx, b, 1, 1); settled.add(b); continue; }
          const life = since / SETTLE;
          const alpha = clampV(life / 0.6, 0, 1);
          const scale = 0.5 + easeOut(clampV(life / 0.7, 0, 1)) * 0.5;
          drawBrick(ctx, b, alpha, scale);
        }
      }
      // progress
      const pct = Math.min(100, Math.round((t / (550 + 1550 + 260)) * 100));
      bootBar.style.width = pct + '%';
      // done
      if (t >= 550 + 1550 + 260){
        bootBar.style.width = '100%';
        boot.classList.add('built');
        setTimeout(() => showRealLogo(), 500);
        if (!BOOT_HOLD) setTimeout(finishBoot, 1650);
        return;
      }
      requestAnimationFrame(tick);
    }
    if (reduced){
      for (const b of BRICKS) drawBrick(sctx, b, 1, 1);
      boot.classList.add('built');
      bootBar.style.width = '100%';
      setTimeout(() => showRealLogo(), 200);
      setTimeout(finishBoot, 900);
    } else {
      requestAnimationFrame(tick);
    }
  }
  buildFist();
'''
new_block = new_block.replace("__MASK__", mask_arr)

html = open(HTML, encoding="utf-8").read()
start_marker = "  /* ── BOOT OVERLAY — the fist builds itself brick by brick ── */"
end_marker = "  } else {\n    buildFist();\n  }"
start = html.index(start_marker)
end = html.index(end_marker) + len(end_marker)
# remove the old listeners-remainder is AFTER this (listeners come after buildFist) - keep them
# The old block ended before the listeners; ensure no leftover duplicate buildFist()
html = html[:start] + new_block + html[end:]
open(HTML, "w", encoding="utf-8", newline="\n").write(html)
# cleanup stray brick references that referenced #brickFist in the source (should be gone)
print("replaced boot. new len:", len(html))
print("brickFixt refs left:", html.count("brickFist"))
print("buildFist dup left:", html.count("function buildFist"))
