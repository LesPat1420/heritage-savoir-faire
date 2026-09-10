/* ==========================================================================
   Galerie chantiers — visionneuse partagée (aucune dépendance)
   Attend window.PROJETS (assets/js/projets.js) chargé avant.
   Câble tout élément [data-projet="<id>"] : au clic, ouvre l'album.
   ========================================================================== */
(function () {
  "use strict";
  var PROJETS = window.PROJETS || [];
  if (!PROJETS.length) return;

  var byId = {};
  PROJETS.forEach(function (p) { byId[p.id] = p; });

  var CAM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 8a2 2 0 0 1 2-2h2l1.4-2h7.2L20 6h1a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2z"/><circle cx="12" cy="12.5" r="3.5"/></svg>';

  /* ---- badge « N photos » sur chaque vignette ---- */
  var triggers = [].slice.call(document.querySelectorAll('[data-projet]'));
  triggers.forEach(function (el) {
    var p = byId[el.getAttribute('data-projet')];
    if (!p) return;
    var n = p.photos.length;
    if (!el.querySelector('.shot-count')) {
      var b = document.createElement('span');
      b.className = 'shot-count';
      b.innerHTML = CAM + '<span>' + n + (n > 1 ? ' photos' : ' photo') + '</span>';
      el.appendChild(b);
    }
    if (el.tagName === 'BUTTON') {
      el.type = 'button';
      el.setAttribute('aria-label', 'Voir le chantier : ' + p.titre + ' (' + n + ' photos)');
    }
    el.addEventListener('click', function (e) {
      e.preventDefault();
      open(p.id, 0, el);
    });
  });
  if (!triggers.length) return;

  /* ---- construction de l'overlay (une seule fois) ---- */
  var lb = document.createElement('div');
  lb.className = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.setAttribute('aria-label', 'Photos du chantier');
  lb.innerHTML =
    '<div class="lb-bar">' +
      '<span class="lb-title"></span>' +
      '<span class="lb-counter"></span>' +
      '<button class="lb-close" type="button" aria-label="Fermer">✕</button>' +
    '</div>' +
    '<div class="lb-stage">' +
      '<button class="lb-nav lb-prev" type="button" aria-label="Photo précédente">‹</button>' +
      '<img class="lb-img" alt="">' +
      '<button class="lb-nav lb-next" type="button" aria-label="Photo suivante">›</button>' +
    '</div>' +
    '<p class="lb-cap"></p>' +
    '<div class="lb-film"></div>';
  document.body.appendChild(lb);

  var elTitle = lb.querySelector('.lb-title'),
      elCount = lb.querySelector('.lb-counter'),
      elImg   = lb.querySelector('.lb-img'),
      elCap   = lb.querySelector('.lb-cap'),
      elPrev  = lb.querySelector('.lb-prev'),
      elNext  = lb.querySelector('.lb-next'),
      elFilm  = lb.querySelector('.lb-film'),
      elClose = lb.querySelector('.lb-close');

  var cur = null, idx = 0, lastFocus = null;

  function webpOf(src) { return src.replace(/\.jpg$/i, '.webp'); }

  function render() {
    var ph = cur.photos[idx];
    elImg.onerror = function () { elImg.onerror = null; elImg.src = ph.src; };
    elImg.src = webpOf(ph.src);
    elImg.alt = ph.leg || cur.titre;
    elCap.textContent = ph.leg || '';
    elTitle.textContent = cur.titre;
    elCount.textContent = (idx + 1) + ' / ' + cur.photos.length;
    elPrev.disabled = idx === 0;
    elNext.disabled = idx === cur.photos.length - 1;
    var btns = elFilm.children;
    for (var i = 0; i < btns.length; i++) {
      btns[i].setAttribute('aria-current', i === idx ? 'true' : 'false');
    }
    if (btns[idx]) btns[idx].scrollIntoView({ block: 'nearest', inline: 'center' });
    // préchargement voisins
    [idx - 1, idx + 1].forEach(function (j) {
      if (cur.photos[j]) { var im = new Image(); im.src = webpOf(cur.photos[j].src); }
    });
  }

  function buildFilm() {
    elFilm.innerHTML = '';
    cur.photos.forEach(function (ph, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Photo ' + (i + 1));
      b.innerHTML = '<img src="' + ph.src.replace(/\.jpg$/i, '-t.webp') + '" alt="" loading="lazy" width="120" height="90">';
      b.addEventListener('click', function () { idx = i; render(); });
      elFilm.appendChild(b);
    });
  }

  function open(id, start, trigger) {
    cur = byId[id];
    if (!cur) return;
    idx = start || 0;
    lastFocus = trigger || document.activeElement;
    buildFilm();
    render();
    lb.classList.add('is-open');
    document.body.classList.add('lb-lock');
    document.addEventListener('keydown', onKey);
    elClose.focus();
  }

  function close() {
    lb.classList.remove('is-open');
    document.body.classList.remove('lb-lock');
    document.removeEventListener('keydown', onKey);
    elImg.src = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function step(d) {
    var n = idx + d;
    if (n < 0 || n >= cur.photos.length) return;
    idx = n; render();
  }

  function onKey(e) {
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') step(-1);
    else if (e.key === 'ArrowRight') step(1);
    else if (e.key === 'Tab') {
      var f = lb.querySelectorAll('button');
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  }

  elPrev.addEventListener('click', function () { step(-1); });
  elNext.addEventListener('click', function () { step(1); });
  elClose.addEventListener('click', close);
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb-stage')) close(); });

  // swipe tactile
  var x0 = null;
  lb.querySelector('.lb-stage').addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  lb.querySelector('.lb-stage').addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 45) step(dx < 0 ? 1 : -1);
    x0 = null;
  }, { passive: true });
})();
