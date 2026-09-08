/* ============================================================
   Bois 3D — modèles de charpente (Three.js)
   Usage :  var api = Charpente3D.create(canvas, { interactive:true });
            api.next() / api.prev() / api.setModel(i) / api.getLabel()
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
    const autoSpeed = opts.autoSpeed != null ? opts.autoSpeed : 0.0022;
    let autol = true;

    // vue courante (modifiée par le glisser + le modèle actif)
    const view = {
      dist: opts.dist || 15,
      phi: opts.phi || 1.12,
      theta: opts.theta || 0.7,
      target: new THREE.Vector3(0, 1.4, 0)
    };

    // ---- Lumières ----
    scene.add(new THREE.HemisphereLight(0xfff4e0, 0x6b5a44, 0.85));
    const sun = new THREE.DirectionalLight(0xffe8c4, 1.15);
    sun.position.set(7, 12, 6);
    sun.castShadow = true;
    const sm = opts.shadowMap || 2048;
    sun.shadow.mapSize.set(sm, sm);
    sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
    sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
    scene.add(sun);

    // ---- Sol (ombre uniquement) ----
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(80, 80),
      new THREE.ShadowMaterial({ opacity: opts.shadowOpacity != null ? opts.shadowOpacity : 0.16 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.02;
    ground.receiveShadow = true;
    scene.add(ground);

    // ---- Matériaux bois ----
    const woodLight = new THREE.MeshStandardMaterial({ color: 0xb07b42, roughness: 0.82, metalness: 0.02 });
    const woodDark  = new THREE.MeshStandardMaterial({ color: 0x8a5a2c, roughness: 0.85, metalness: 0.02 });
    const chevMat   = new THREE.MeshStandardMaterial({ color: 0xc08a4e, roughness: 0.8 });
    const pegMat    = new THREE.MeshStandardMaterial({ color: 0x5f3c1f, roughness: 0.7 });
    const plasterMat = new THREE.MeshStandardMaterial({ color: 0xe7dcc3, roughness: 1 });
    const woodPale  = new THREE.MeshStandardMaterial({ color: 0xd7b784, roughness: 0.78, metalness: 0.02 });
    const woodAged  = new THREE.MeshStandardMaterial({ color: 0x6a5233, roughness: 0.92, metalness: 0.02 });

    function beam(len, h, d, mat) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(len, h, d), mat || woodLight);
      m.castShadow = true; m.receiveShadow = true;
      return m;
    }
    function box(g, w, h, d, x, y, z, mat) {
      const m = beam(w, h, d, mat);
      m.position.set(x, y, z);
      g.add(m);
      return m;
    }
    function member(group, x1, y1, x2, y2, h, d, mat) {
      const dx = x2 - x1, dy = y2 - y1;
      const b = beam(Math.hypot(dx, dy), h, d, mat);
      b.position.set((x1 + x2) / 2, (y1 + y2) / 2, 0);
      b.rotation.z = Math.atan2(dy, dx);
      group.add(b);
    }

    /* ========== Modèle 1 : ferme à poinçon ========== */
    function buildFerme() {
      const g = new THREE.Group();
      const SPAN = 8, HALF = SPAN / 2, RISE = 3.1, FOOT = 0;

      function makeFerme(z) {
        const f = new THREE.Group();
        member(f, -HALF, FOOT, HALF, FOOT, 0.42, 0.34, woodDark);
        member(f, -HALF, FOOT, 0, RISE, 0.38, 0.3);
        member(f,  HALF, FOOT, 0, RISE, 0.38, 0.3);
        member(f, 0, FOOT, 0, RISE, 0.34, 0.34, woodDark);
        member(f, 0, RISE * 0.42, -HALF * 0.52, RISE * 0.52, 0.26, 0.24);
        member(f, 0, RISE * 0.42,  HALF * 0.52, RISE * 0.52, 0.26, 0.24);
        member(f, 0, RISE * 0.42, -HALF * 0.22, FOOT + 0.9, 0.2, 0.22);
        member(f, 0, RISE * 0.42,  HALF * 0.22, FOOT + 0.9, 0.2, 0.22);
        f.position.z = z;
        return f;
      }

      const Z = opts.fermes || [-3, 0, 3];
      Z.forEach((z) => g.add(makeFerme(z)));

      const spanZ = Z[Z.length - 1] - Z[0] + 1.2;
      function longBeam(x, y, h, d, mat) {
        const m = beam(spanZ, h, d, mat);
        m.rotation.y = Math.PI / 2;
        m.position.set(x, y, 0);
        g.add(m);
      }
      longBeam(-HALF, FOOT, 0.3, 0.3, woodDark);
      longBeam( HALF, FOOT, 0.3, 0.3, woodDark);
      longBeam(0, RISE - 0.02, 0.26, 0.26, woodDark);
      const px = -HALF * 0.5, py = FOOT + RISE * 0.5;
      longBeam(px, py + 0.15, 0.22, 0.22);
      longBeam(-px, py + 0.15, 0.22, 0.22);

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
          g.add(c);
        }
      }

      return {
        group: g, name: 'Ferme à poinçon',
        target: new THREE.Vector3(0, RISE * 0.45, 0),
        dist: opts.dist || 15, phi: opts.phi || 1.12, theta: 0.7
      };
    }

    /* ========== Modèle 2 : assemblage tenon-mortaise ========== */
    function buildAssemblage() {
      const g = new THREE.Group();

      // poteau vertical (section 1 x 1), percé d'une mortaise traversante
      const H = 4.4, MY0 = 2.0, MY1 = 2.8;       // hauteur de la mortaise
      box(g, 1, MY0, 1, 0, MY0 / 2, 0, woodLight);                       // fût sous la mortaise
      box(g, 1, H - MY1, 1, 0, (H + MY1) / 2, 0, woodLight);             // fût au-dessus
      box(g, 1, MY1 - MY0, 0.34, 0, (MY0 + MY1) / 2,  0.33, woodLight);  // joue avant
      box(g, 1, MY1 - MY0, 0.34, 0, (MY0 + MY1) / 2, -0.33, woodLight);  // joue arrière

      // traverse horizontale qui vient s'emboîter, tenon traversant + about débordant
      const beamY = 2.4;
      box(g, 4, 0.85, 0.85, -2.5, beamY, 0, woodDark);   // corps de la traverse
      box(g, 1.9, 0.5, 0.32, 0.45, beamY, 0, woodDark);  // tenon (traverse la mortaise et dépasse)

      // cheville qui bloque l'assemblage (dépasse en haut et en bas)
      const peg = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 1.5, 14), pegMat);
      peg.castShadow = true; peg.receiveShadow = true;
      peg.position.set(0.62, beamY, 0);
      g.add(peg);

      return {
        group: g, name: 'Tenon-mortaise',
        target: new THREE.Vector3(0, beamY + 0.1, 0),
        dist: 10.5, phi: 1.22, theta: 0.72
      };
    }

    /* ========== Modèle 3 : pan de bois (colombage) ========== */
    function buildColombage() {
      const g = new THREE.Group();
      const W = 3, TOP = 4;

      // remplissage (torchis) légèrement en retrait
      box(g, W, TOP, 0.18, -W / 2, TOP / 2, -0.12, plasterMat);
      box(g, W, TOP, 0.18,  W / 2, TOP / 2, -0.12, plasterMat);

      // sablières haute et basse
      member(g, -W, 0, W, 0, 0.34, 0.42, woodDark);
      member(g, -W, TOP, W, TOP, 0.34, 0.42, woodDark);
      // poteaux
      member(g, -W, 0, -W, TOP, 0.34, 0.4, woodLight);
      member(g,  0, 0,  0, TOP, 0.34, 0.4, woodLight);
      member(g,  W, 0,  W, TOP, 0.34, 0.4, woodLight);
      // décharges (écharpes) en V
      member(g, -W, 0, 0, TOP, 0.26, 0.3, woodLight);
      member(g,  W, 0, 0, TOP, 0.26, 0.3, woodLight);
      // tournisses (petits bois horizontaux)
      member(g, -W, TOP * 0.5, 0, TOP * 0.5, 0.2, 0.28, woodLight);
      member(g,  0, TOP * 0.5, W, TOP * 0.5, 0.2, 0.28, woodLight);

      return {
        group: g, name: 'Pan de bois',
        target: new THREE.Vector3(0, TOP * 0.5, 0),
        dist: 13.5, phi: 1.28, theta: 0.62
      };
    }

    /* ========== Modèle 4 : une seule poutre, taillée ==========
       d'après une photo d'atelier de Lou : UNE poutre équarrie, dont on a
       taillé (1) un about évasé « en trompette » (galbe concave sous la pièce,
       dessus plat, pied large) et (2) une entaille à mi-bois en travers du
       dessus, sur toute la largeur, pour recevoir une pièce croisée.
       Le corps neuf est clair, la partie ancienne au-delà de l'entaille est grise. */
    function buildMoise() {
      const g = new THREE.Group();

      const W = 1.6;                 // largeur de la poutre (axe Z)

      // --- profil latéral de la zone taillée (about + entaille), extrudé sur W ---
      const s = new THREE.Shape();
      s.moveTo(0.16, 0.36);                                   // nez de l'about évasé
      s.quadraticCurveTo(0.75, 0.56, 1.75, 0.62);             // dessus qui remonte du nez au corps
      s.lineTo(3.15, 0.66);                                   // dessus jusqu'à l'entaille
      s.lineTo(3.18, 0.02);                                   // joue avant de l'entaille (verticale)
      s.lineTo(5.55, 0.00);                                   // fond de l'entaille (mi-hauteur)
      s.lineTo(5.62, 0.70);                                   // joue arrière de l'entaille
      s.lineTo(5.62, -0.58);                                  // about de raccord (contre la partie grise)
      s.lineTo(1.35, -0.58);                                  // dessous du corps : droit sur presque toute la longueur
      s.quadraticCurveTo(0.92, -0.78, 0.74, -1.22);           // galbe concave, serré près de la pointe...
      s.quadraticCurveTo(0.58, -1.52, 0.42, -1.60);           // ...jusqu'au pied évasé
      s.lineTo(0.16, -1.62);                                  // méplat du pied
      s.lineTo(0.16, 0.36);                                   // grande face d'about verticale
      s.closePath();

      const eg = new THREE.ExtrudeGeometry(s, {
        depth: W, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.05, bevelSegments: 1, curveSegments: 26
      });
      eg.translate(0, 0, -W / 2);
      const worked = new THREE.Mesh(eg, woodPale);
      worked.castShadow = true; worked.receiveShadow = true;
      g.add(worked);

      // --- prolongement ancien (gris), au-delà de l'entaille ---
      box(g, 4.6, 1.29, W, 7.9, 0.075, 0, woodAged);

      // recentrage : la zone d'intérêt est vers x = 0..6
      g.position.x = -3.1;

      return {
        group: g, name: 'Croisement à mi-bois',
        target: new THREE.Vector3(0, -0.25, 0),
        dist: 12.5, phi: 1.22, theta: 0.72
      };
    }

    const BUILDERS = [buildFerme, buildAssemblage, buildColombage, buildMoise];
    let modelIndex = Math.min(opts.model || 0, BUILDERS.length - 1);
    let current = null, currentName = '';

    function disposeGroup(g) {
      g.traverse((o) => { if (o.geometry) o.geometry.dispose(); });
    }

    function setModel(i, keepAngle) {
      modelIndex = ((i % BUILDERS.length) + BUILDERS.length) % BUILDERS.length;
      if (current) { scene.remove(current); disposeGroup(current); }
      const m = BUILDERS[modelIndex]();
      current = m.group;
      currentName = m.name;
      scene.add(current);
      view.target.copy(m.target);
      view.dist = m.dist;
      view.phi = m.phi;
      if (!keepAngle) view.theta = m.theta;
      autol = true;
      render();
    }

    function getLabel() { return currentName; }

    // ---- Interaction ----
    if (interactive) {
      canvas.style.touchAction = 'none';
      let dragging = false, mx = 0, my = 0;
      canvas.addEventListener('pointerdown', (e) => { dragging = true; autol = false; mx = e.clientX; my = e.clientY; canvas.setPointerCapture(e.pointerId); });
      canvas.addEventListener('pointerup', () => { dragging = false; });
      canvas.addEventListener('pointermove', (e) => {
        if (!dragging) return;
        view.theta -= (e.clientX - mx) * 0.008;
        view.phi = Math.max(0.35, Math.min(1.5, view.phi - (e.clientY - my) * 0.006));
        mx = e.clientX; my = e.clientY;
      });
      if (opts.wheelZoom) {
        canvas.addEventListener('wheel', (e) => {
          e.preventDefault();
          view.dist = Math.max(6, Math.min(28, view.dist + Math.sign(e.deltaY) * 1.1));
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

    function render() {
      resize();
      if (autol && !reduce) view.theta += autoSpeed;
      camera.position.set(
        view.dist * Math.sin(view.phi) * Math.sin(view.theta),
        view.dist * Math.cos(view.phi),
        view.dist * Math.sin(view.phi) * Math.cos(view.theta)
      );
      camera.lookAt(view.target);
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

    setModel(modelIndex, true);   // construit le premier modèle + première image

    return {
      start, stop, render, setModel, getLabel,
      count: BUILDERS.length,
      next: () => setModel(modelIndex + 1),
      prev: () => setModel(modelIndex - 1)
    };
  }

  return { create };
})();
