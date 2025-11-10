// Lightweight enhancements for greenspace page
// - Renders description, amenity badges, and "good for" chips
// - Shows a small seasonal highlight based on actual trees in bounds
(function(){
  function onReady(fn){
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn, { once: true });
    else fn();
  }

  const AMENITY_MAP = [
    { key: 'water', test: /water|fountain|lily|pond/i, emoji: '🚰', label: 'Water' },
    { key: 'bench', test: /bench/i, emoji: '🪑', label: 'Benches' },
    { key: 'shade', test: /shade/i, emoji: '🌳', label: 'Shade' },
    { key: 'trail', test: /trail|path|walkway/i, emoji: '🥾', label: 'Paths/Trails' },
    { key: 'open',  test: /open grass|lawn|field/i, emoji: '🌿', label: 'Open Lawn' },
    { key: 'garden', test: /garden|native plants|flowers/i, emoji: '🌸', label: 'Garden' },
    { key: 'wifi', test: /wifi/i, emoji: '📶', label: 'Wi‑Fi Nearby' },
    { key: 'food', test: /food|student center/i, emoji: '🍴', label: 'Food Nearby' },
    { key: 'bike', test: /bike/i, emoji: '🚲', label: 'Bike Rack' },
    { key: 'quiet', test: /quiet|less crowded/i, emoji: '🤫', label: 'Quiet Corners' },
    { key: 'art', test: /art/i, emoji: '🖼️', label: 'Art' }
  ];

  // Friendly per-greenspace placeholders keyed by SVG id/name
  const PLACEHOLDERS = {
    // TODO: refine amenities/description later for Limestone_Lawn
    Limestone_Lawn: {
      description: 'A calm open lawn popular for quick breaks and casual meetups.',
      features: ['Open Grass Area', 'Shade Trees', 'Benches', 'Paths'],
      goodfor: ['Reading', 'Hang out', 'Walking']
    },
    // TODO: refine amenities/description later for Gatton_Bls
    Gatton_Bls: {
      description: 'Greens around Gatton College.',
      features: ['Shade Trees', 'Gardens'],
      goodfor: ['Study spot', 'Walking']
    },
    // TODO: refine amenities/description later for Ezra_Bldg
    Ezra_Bldg: {
      description: 'Pocket green near the Ezra building.',
      features: ['Open Grass Area', 'Benches'],
      goodfor: ['Relaxing', 'Reading']
    },
    // TODO: refine amenities/description later for Art_Center
    Art_Center: {
      description: 'Art-adjacent lawn with visual interest.',
      features: ['Art Installations', 'Shade Trees', 'Benches'],
      goodfor: ['Photography', 'Walking']
    },
    // TODO: refine amenities/description later for Art_Lib
    Art_Lib: {
      description: 'Green strip by the art library.',
      features: ['Benches', 'Shade Trees', 'Paths'],
      goodfor: ['Study spot', 'Meditation']
    },
    // TODO: refine amenities/description later for Patterson_OT
    Patterson_OT: {
      description: 'Outdoor pathway near the Student Center.',
      features: ['Benches', 'Less Crowded', 'Paths'],
      goodfor: ['Walking', 'Meditation']
    },
    // TODO: refine amenities/description later for Gatton_SC
    Gatton_SC: {
      description: 'Student Center seating green.',
      features: ['Nearby Food', 'Seating', 'Bike Racks'],
      goodfor: ['Hang out', 'Picnic']
    },
    // TODO: refine amenities/description later for Old_Engineer
    Old_Engineer: {
      description: 'Historic corridor of trees and lawn.',
      features: ['Shade Trees', 'Paths', 'Benches'],
      goodfor: ['Walking', 'Reading']
    },
    // TODO: refine amenities/description later for President
    President: {
      description: 'Serene garden near the President’s area.',
      features: ['Lily Pond', 'Native Plants', 'Benches', 'Shade Trees'],
      goodfor: ['Meditation', 'Photography']
    },
    // TODO: refine amenities/description later for Mining
    Mining: {
      description: 'Small lawn near the mining area.',
      features: ['Open Grass Area', 'Shade Trees'],
      goodfor: ['Relaxing']
    },
    // TODO: refine amenities/description later for Dorms
    Dorms: {
      description: 'Residential-side green corridor.',
      features: ['Paths', 'Shade Trees', 'Open Grass Area'],
      goodfor: ['Jogging', 'Walking']
    },
    // TODO: refine amenities/description later for Funkhouser
    Funkhouser: {
      description: 'Shaded path by Funkhouser.',
      features: ['Shaded Trees', 'Study Spots', 'Benches'],
      goodfor: ['Study spot', 'Walking']
    },
    // TODO: refine amenities/description later for FPAT_Alcove
    FPAT_Alcove: {
      description: 'FPAT-adjacent alcove with pockets of shade.',
      features: ['Shade Trees', 'Benches'],
      goodfor: ['Reading', 'Relaxing']
    },
    // TODO: refine amenities/description later for WT_Young
    WT_Young: {
      description: 'WT Young Library lawn — open and study-friendly.',
      features: ['Open Grass Area', 'Study Spots', 'WiFi Access', 'Natural Shade'],
      goodfor: ['Study spot', 'Reading', 'Hang out']
    },
    // TODO: refine amenities/description later for Memorial
    Memorial: {
      description: 'Green near the Memorial area.',
      features: ['Paths', 'Shade Trees'],
      goodfor: ['Walking']
    },
    // TODO: refine amenities/description later for White_Hall
    White_Hall: {
      description: 'Green spine by White Hall.',
      features: ['Paths', 'Benches', 'Shade Trees'],
      goodfor: ['Walking', 'Study spot']
    }
  };

  // Derive activity chips from amenities/features
  function deriveActivities(text){
    const s = (text || '').toLowerCase();
    const chips = new Set();
    if (/trail|path|walkway/.test(s)) chips.add('Walking');
    if (/open grass|lawn|field|shade/.test(s)) chips.add('Reading');
    if (/open grass|lawn|field/.test(s)) chips.add('Hang out');
    if (/bench/.test(s)) chips.add('Relaxing');
    if (/quiet|less crowded/.test(s)) chips.add('Meditation');
    if (/wifi|study/.test(s)) chips.add('Study spot');
    if (/bike/.test(s)) chips.add('Cycling');
    if (/garden|flowers|native plants/.test(s)) chips.add('Photography');
    if (/food|student center/.test(s)) chips.add('Picnic');
    return Array.from(chips);
  }

  function dedupe(arr){ return Array.from(new Set(arr.filter(Boolean))); }

  // Seasonal species facts (tiny, client-side)
  const SPECIES_FACTS = [
    { key: 'ginkgo', test: /(ginkgo|gingko)/i, label: 'Ginkgo', fact: 'Fan-shaped leaves turn brilliant gold in fall.' },
    { key: 'maple', test: /(acer|maple)/i, label: 'Maple', fact: 'Known for vivid reds and oranges in fall.' },
    { key: 'sweetgum', test: /(liquidambar|sweet\s?gum)/i, label: 'Sweetgum', fact: 'Star-shaped leaves with rainbow fall color.' },
    { key: 'baldcypress', test: /(taxodium|bald\s?cypress)/i, label: 'Bald cypress', fact: 'Rusty needles in late fall; a deciduous conifer.' },
    { key: 'oak', test: /(quercus|oak)/i, label: 'Oak', fact: 'Strong structure; many species with lasting fall leaves.' },
    { key: 'beech', test: /(fagus|beech)/i, label: 'Beech', fact: 'Coppery leaves often persist into winter.' },
    { key: 'holly', test: /(ilex|holly)/i, label: 'Holly', fact: 'Glossy evergreen leaves; bright berries in winter.' },
    { key: 'spruce', test: /(picea|spruce)/i, label: 'Spruce', fact: 'Evergreen spires add winter color and shelter.' },
    { key: 'cedar', test: /(cedrus|juniperus|cedar|juniper)/i, label: 'Cedar/Juniper', fact: 'Fragrant evergreen foliage carries through winter.' },
    { key: 'pine', test: /(pinus|pine)/i, label: 'Pine', fact: 'Year‑round green needles; calming scent.' }
  ];

  function speciesFactFor(tree){
    const s = `${tree.latin_name || ''} ${tree.common_name || ''}`;
    const f = SPECIES_FACTS.find(x => x.test.test(s));
    return f || null;
  }

  function currentSeasonKey(month){
    // 0-1 winter; 2-4 spring; 5-7 summer; 8-9 fall; 10-11 late_fall
    if (month === 10 || month === 11) return 'late_fall';
    if (month === 0 || month === 1) return 'winter';
    if (month >= 2 && month <= 4) return 'spring';
    if (month >= 5 && month <= 7) return 'summer';
    return 'fall';
  }

  const SEASON_KEYS = {
    late_fall: ['ginkgo','maple','sweetgum','baldcypress','oak','beech'],
    winter: ['holly','spruce','cedar','pine','beech','oak'],
    fall: ['maple','sweetgum','oak','ginkgo','baldcypress'],
    spring: ['maple','oak','spruce','cedar','pine'],
    summer: ['oak','spruce','cedar','pine']
  };

  function pickSeasonalCandidates(trees){
    const m = new Date().getMonth();
    const key = currentSeasonKey(m);
    const allowed = new Set(SEASON_KEYS[key] || []);
    const all = [];
    trees.forEach(t => {
      const f = speciesFactFor(t);
      if (!f) return;
      if (!allowed.size || allowed.has(f.key)) {
        all.push({ tree: t, fact: f });
      }
    });
    // random sample up to 4
    for (let i = all.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [all[i], all[j]] = [all[j], all[i]];
    }
    return all.slice(0, Math.min(4, all.length));
  }

  let rotateTimer = null;
  function showSeasonal(items, index){
    const wrap = document.getElementById('gs-seasonal');
    const imgWrap = wrap ? wrap.querySelector('.s-img img') : null;
    const titleEl = document.getElementById('gs-season-title');
    const textEl = document.getElementById('gs-season-text');
    if (!wrap || !titleEl || !textEl) return;
    if (!items || !items.length) {
      // fallback generic
      titleEl.textContent = 'Seasonal highlight';
      textEl.textContent = 'Explore trees in this space — more highlights coming soon.';
      wrap.hidden = false;
      return;
    }
    const it = items[index % items.length];
    const t = it.tree;
    const icon = (window.treeIcons && window.treeIcons.getIconUrl) ? window.treeIcons.getIconUrl(t.latin_name, t.common_name) : '';
    if (imgWrap && icon) { imgWrap.src = icon; imgWrap.alt = `${t.common_name || it.fact.label}`; }
    titleEl.textContent = `${it.fact.label} near you`;
    textEl.textContent = it.fact.fact;
    wrap.hidden = false;
    try { wrap.classList.remove('pulse'); void wrap.offsetWidth; wrap.classList.add('pulse'); } catch(_) {}
  }

  function startRotation(items){
    if (rotateTimer) { try { clearInterval(rotateTimer); } catch(e) {} rotateTimer = null; }
    if (!items || !items.length) { showSeasonal(items, 0); return; }
    let idx = 0;
    showSeasonal(items, idx);
    rotateTimer = setInterval(() => { idx = (idx + 1) % items.length; showSeasonal(items, idx); }, 8000);
  }

  // Expose a tiny seasonal updater called by the page after tree fetch
  window.gsSeasonal = {
    update(trees, name){
      try {
        const items = pickSeasonalCandidates(Array.isArray(trees) ? trees : []);
        startRotation(items);
      } catch (e) { /* ignore */ }
    }
  };

  onReady(function(){
    const t = document.getElementById('gs-data');
    if (!t) return;
    const metaRaw = t.dataset.meta || '';
    const name = t.dataset.name || 'Greenspace';
    let meta = null;
    try { meta = metaRaw ? JSON.parse(metaRaw) : null; } catch(_) { meta = null; }
    // Fallback to friendly placeholders by SVG id/name
    if (!meta && PLACEHOLDERS[name]) meta = PLACEHOLDERS[name];
    if (!meta) {
      const pretty = String(name || 'this greenspace').replace(/_/g, ' ');
      // TODO: refine generic fallback copy later
      meta = {
        description: `A campus greenspace: ${pretty}.`,
        features: ['Open Grass Area', 'Shade Trees', 'Paths'],
        goodfor: ['Walking', 'Reading', 'Hang out']
      };
    }

    const descEl = document.getElementById('gs-desc') || document.getElementById('gs-desc-header');
    const amEl = document.getElementById('gs-amenities');
    const gfEl = document.getElementById('gs-goodfor');
    const sWrap = document.getElementById('gs-seasonal');
    const sTitle = document.getElementById('gs-season-title');
    const sText = document.getElementById('gs-season-text');

    const features = Array.isArray(meta?.features) ? meta.features : [];
    const desc = (meta && meta.description) ? meta.description : `Tell a short story about ${name}.`;

    // Description
    if (descEl) descEl.textContent = desc;

    // Breeze toggle (ambient gradient + very quiet rustling loop)
    (function setupBreeze(){
      const btn = document.getElementById('breeze-toggle');
      const container = document.querySelector('.gs-container');
      if (!btn || !container) return;
      const audioUrl = (window.gsBreeze && window.gsBreeze.url) || '/static/audio/explore-rustling.mp3';
      let a = null; let on = false;
      function ensure(){ if (!a) { try { a = new Audio(audioUrl); a.loop = true; a.volume = 0.05; } catch(_) { a = null; } } }
      function toggle(){
        on = !on;
        btn.setAttribute('aria-pressed', String(on));
        container.classList.toggle('breeze', on);
        if (navigator.vibrate) { try { navigator.vibrate(on ? 6 : 3); } catch(_) {} }
        try {
          ensure();
          if (a) {
            if (on) { a.currentTime = 0; a.play().catch(()=>{}); }
            else { a.pause(); }
          }
        } catch(_) {}
      }
      btn.addEventListener('click', toggle);
      document.addEventListener('visibilitychange', () => { try { if (document.hidden && a) a.pause(); } catch(_) {} });
    })();

    // Soft haptic when interacting with seasonal banner
    (function setupSeasonalHaptics(){
      const card = document.getElementById('gs-season-card');
      if (!card) return;
      card.addEventListener('click', () => { try { if (navigator.vibrate) navigator.vibrate(8); } catch(_) {} });
    })();

    // Amenities
    const amenityTokens = [];
    if (features.length) {
      features.forEach(f => {
        const found = AMENITY_MAP.find(a => a.test.test(String(f)));
        if (found) amenityTokens.push(found.key);
      });
    }
    // Also try description text to infer amenities
    AMENITY_MAP.forEach(a => { if (a.test.test(desc)) amenityTokens.push(a.key); });
    const finalAm = dedupe(amenityTokens).map(k => AMENITY_MAP.find(a => a.key === k));

    if (amEl) {
      amEl.innerHTML = '';
      if (!finalAm.length) {
        amEl.innerHTML = '<span style="opacity:.8">No amenities recorded yet.</span>';
      } else {
        finalAm.forEach(a => {
          const el = document.createElement('span');
          el.className = 'amenity';
          el.innerHTML = `<span class="a-emoji" aria-hidden="true">${a.emoji}</span><span>${a.label}</span>`;
          el.title = a.label;
          amEl.appendChild(el);
        });
      }
    }

    // Activities
    const activityList = dedupe([
      ...(Array.isArray(meta?.goodfor) ? meta.goodfor : []),
      ...deriveActivities(features.join(' | ')),
      ...deriveActivities(desc)
    ]);
    if (gfEl) {
      gfEl.innerHTML = '';
      if (!activityList.length) {
        gfEl.innerHTML = '<span style="opacity:.8">We will add suggestions here.</span>';
      } else {
        activityList.forEach(lbl => {
          const chip = document.createElement('span');
          chip.className = 'chip';
          chip.textContent = lbl;
          gfEl.appendChild(chip);
        });
      }
    }

    // Seasonal highlight is populated after trees are fetched via window.gsSeasonal.update
  });
})();
