/* ============================================================
   Charpente 3D — ferme traditionnelle à poinçon (Three.js)
   Usage :  Charpente3D.create(canvasElement, { interactive:true })
   Nécessite three.min.js chargé avant ce fichier.
   ============================================================ */
window.Charpente3D = (function () {

  function create(canvas, opts) {
    opts = opts || {};
    if (!window.THREE || !canvas) return null;

    const interactive = opts.interactive !== false ? !!opts.interactive : false;
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, opts.maxDPR || 1.75));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(opts.fov || 38, 1, 0.1, 100);
    let camDist = opts.dist || 15;
    let camPhi = opts.phi || 1.12;
    let camTheta = opts.theta || 0.7;
    const autoSpeed = opts.autoSpeed != null ? opts.autoSpeed : 0.0022;
    let autol = true;

    // ---- Lumières ----
    scene.add(new THREE.HemisphereLight(0xfff4e0, 0x6b5a44, 0.85));
    const sun = new THREE.DirectionalLight(0xffe8c4, 1.15);
    sun.position.set(7, 12, 6);
    sun.castShadow = true;
    const sm = opts.shadowMap || 2048;
    sun.shadow.mapSize.set(sm, sm);
    sun.shadow.camera.left = -10; sun.shadow.camera.right = 10;
    sun.shadow.camera.top = 10; sun.shadow.camera.bottom = -10;
    scene.add(sun);

    // ---- Sol (ombre uniquement) ----
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(60, 60),
      new THREE.ShadowMaterial({ opacity: opts.shadowOpacity != null ? opts.shadowOpacity : 0.16 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.02;
    ground.receiveShadow = true;
    scene.add(ground);

    // ---- Bois ----
    const woodLight = new THREE.MeshStandardMaterial({ color: 0xb07b42, roughness: 0.82, metalness: 0.02 });
    const woodDark  = new THREE.MeshStandardMaterial({ color: 0x8a5a2c, roughness: 0.85, metalness: 0.02 });
    const chevMat   = new THREE.MeshStandardMaterial({ color: 0xc08a4e, roughness: 0.8 });

    const truss = new THREE.Group();

    function beam(len, h, d, mat) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(len, h, d), mat || woodLight);
      m.castShadow = true; m.receiveShadow = true;
      return m;
    }
    function member(group, x1, y1, x2, y2, h, d, mat) {
      const dx = x2 - x1, dy = y2 - y1;
      const b = beam(Math.hypot(dx, dy), h, d, mat);
      b.position.set((x1 + x2) / 2, (y1 + y2) / 2, 0);
      b.rotation.z = Math.atan2(dy, dx);
      group.add(b);
    }

    const SPAN = 8, HALF = SPAN / 2, RISE = 3.1, FOOT = 0;

    function makeFerme(z) {
      const f = new THREE.Group();
      member(f, -HALF, FOOT, HALF, FOOT, 0.42, 0.34, woodDark);          // entrait
      member(f, -HALF, FOOT, 0, RISE, 0.38, 0.3);                        // arbalétrier g
      member(f,  HALF, FOOT, 0, RISE, 0.38, 0.3);                        // arbalétrier d
      member(f, 0, FOOT, 0, RISE, 0.34, 0.34, woodDark);                 // poinçon
      member(f, 0, RISE * 0.42, -HALF * 0.52, RISE * 0.52, 0.26, 0.24);  // contrefiche g
      member(f, 0, RISE * 0.42,  HALF * 0.52, RISE * 0.52, 0.26, 0.24);  // contrefiche d
      member(f, 0, RISE * 0.42, -HALF * 0.22, FOOT + 0.9, 0.2, 0.22);    // aisselier g
      member(f, 0, RISE * 0.42,  HALF * 0.22, FOOT + 0.9, 0.2, 0.22);    // aisselier d
      f.position.z = z;
      return f;
    }

    const Z = opts.fermes || [-3, 0, 3];
    Z.forEach((z) => truss.add(makeFerme(z)));

    const spanZ = Z[Z.length - 1] - Z[0] + 1.2;
    function longBeam(x, y, h, d, mat) {
      const m = beam(spanZ, h, d, mat);
      m.rotation.y = Math.PI / 2;
      m.position.set(x, y, 0);
      truss.add(m);
    }
    longBeam(-HALF, FOOT, 0.3, 0.3, woodDark);   // sablière g
    longBeam( HALF, FOOT, 0.3, 0.3, woodDark);   // sablière d
    longBeam(0, RISE - 0.02, 0.26, 0.26, woodDark); // faîtière
    const px = -HALF * 0.5, py = FOOT + RISE * 0.5;
    longBeam(px, py + 0.15, 0.22, 0.22);          // panne g
    longBeam(-px, py + 0.15, 0.22, 0.22);         // panne d

    // ---- Chevrons ----
    const slopeLen = Math.hypot(HALF, RISE);
    const overhang = 0.7;
    const nChev = opts.chevrons || 8;
    for (const s of [-1, 1]) {
      const dx = (s * HALF) / slopeLen, dy = -RISE / slopeLen;
      const nx = -dy, ny = dx;
      const L = slopeLen + overhang;
      const cx = dx * (L / 2) + nx * 0.16;
      const cy = RISE + dy * (L / 2) + ny * 0.16;
      for (let i = 0; i < nChev; i++) {
        const cz = Z[0] - 0.4 + (i / (nChev - 1)) * (spanZ - 0.4);
        const c = beam(L, 0.12, 0.15, chevMat);
        c.position.set(cx, cy, cz);
        c.rotation.z = Math.atan2(dy, dx);
        truss.add(c);
      }
    }

    scene.add(truss);

    // ---- Interaction ----
    if (interactive) {
      canvas.style.touchAction = 'none';
      let dragging = false, mx = 0, my = 0;
      canvas.addEventListener('pointerdown', (e) => { dragging = true; autol = false; mx = e.clientX; my = e.clientY; canvas.setPointerCapture(e.pointerId); });
      canvas.addEventListener('pointerup', () => { dragging = false; });
      canvas.addEventListener('pointermove', (e) => {
        if (!dragging) return;
        camTheta -= (e.clientX - mx) * 0.008;
        camPhi = Math.max(0.35, Math.min(1.5, camPhi - (e.clientY - my) * 0.006));
        mx = e.clientX; my = e.clientY;
      });
      if (opts.wheelZoom) {
        canvas.addEventListener('wheel', (e) => {
          e.preventDefault();
          camDist = Math.max(8, Math.min(26, camDist + Math.sign(e.deltaY) * 1.1));
        }, { passive: false });
      }
    }

    function resize() {
      const w = canvas.clientWidth, h = canvas.clientHeight;
      if (!w || !h) return;
      if (canvas.width !== Math.round(w * renderer.getPixelRatio()) ||
          canvas.height !== Math.round(h * renderer.getPixelRatio())) {
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      }
    }

    const target = new THREE.Vector3(0, RISE * 0.45, 0);
    function render() {
      resize();
      if (autol && !reduce) camTheta += autoSpeed;
      camera.position.set(
        camDist * Math.sin(camPhi) * Math.sin(camTheta),
        camDist * Math.cos(camPhi),
        camDist * Math.sin(camPhi) * Math.cos(camTheta)
      );
      camera.lookAt(target);
      renderer.render(scene, camera);
    }

    // ---- Boucle : ne tourne que visible et onglet actif ----
    let running = false, raf = 0, onScreen = false;
    function loop() { render(); raf = requestAnimationFrame(loop); }
    function start() { if (running || !onScreen || document.hidden) return; running = true; loop(); }
    function stop() { running = false; cancelAnimationFrame(raf); }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver((es) => {
        onScreen = es[0].isIntersecting;
        onScreen ? start() : stop();
      }, { threshold: 0.01 }).observe(canvas);
    } else {
      onScreen = true; start();
    }
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stop(); else start();
    });
    render(); // première image fixe même à l'arrêt

    return { start, stop, render };
  }

  return { create };
})();
