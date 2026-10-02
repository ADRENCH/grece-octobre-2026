// Liste « Qui fait quoi » partagée via /api/todo (fonction Netlify).
// Sans API (aperçu Claude, fichier local), elle bascule en mode local sur l'appareil.
(function(){
  var API = '/api/todo';
  var TASKS = [
    {id:'van', t:'Louer le van 9 places (ou 2 voitures)', d:'Prise dim. 4 à l’aéroport, retour dim. 11. Version longue, carte de crédit du conducteur.', when:'aujourd’hui', now:true},
    {id:'ferries', t:'Ferries Rafina ⇄ Mykonos pour 7', d:'Mer. 7 à 14 h 20, jeu. 8 à 16 h 15 · Ferryhopper ou Seajets.', when:'aujourd’hui', now:true},
    {id:'acropole', t:'Billets Acropole, sam. 10 à 8 h', d:'hhticket.gr · 7 billets nominatifs, 30 € chacun.', when:'cette semaine', now:true},
    {id:'myk', t:'Voitures ou quads à Mykonos', d:'Livrés au nouveau port mer. 7 à 17 h, rendus jeu. 8 vers 15 h.', when:'avant le 7'},
    {id:'parking', t:'Parking à Rafina', d:'Safe Park Harbour, +30 22940 25104 · du mer. 7 au jeu. 8.', when:'avant le 7'},
    {id:'caution', t:'300 € en espèces pour la caution de Mykonos', d:'Un seul porteur pour le groupe, à rembourser entre vous.', when:'avant le 7'},
    {id:'vin', t:'Dégustation Lafazanis, mar. 6 vers 14 h 30', d:'Domaine à Némée, réservation obligatoire.', when:'avant le 6'},
    {id:'delos', t:'Bateau pour Délos, jeu. 8 à 10 h', d:'Delos Tours, vieux port · vérifier qu’il part bien le jeudi.', when:'avant le 8'},
    {id:'tables', t:'Tables pour 7', d:'O Noulis à Nauplie (dim. 4), rooftop à Monastiraki (sam. 3, les 4).', when:'au fil de l’eau'}
  ];
  var NAMES = ['Antonin','Nathan','Xavier','Simon','Erwan','Donovan','Paul'];
  var state = {}, shared = false, filter = 'all', me = '';
  var host = document.getElementById('tasks');
  var meSel = document.getElementById('me');
  var statusEl = document.getElementById('td-status');

  function lsGet(k, d){ try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch(e){ return d; } }
  function lsSet(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} }
  function say(msg, warn){ statusEl.textContent = msg || ''; statusEl.classList.toggle('warn', !!warn); }
  function when(iso){
    if (!iso) return '';
    var d = new Date(iso);
    return d.toLocaleDateString('fr-FR', {weekday:'short', day:'numeric'}) + ' à ' + d.toLocaleTimeString('fr-FR', {hour:'2-digit', minute:'2-digit'});
  }

  me = lsGet('gr-me', '') || '';
  filter = lsGet('gr-filter', 'all') || 'all';
  meSel.value = me;

  TASKS.forEach(function(t){
    var row = document.createElement('div');
    row.className = 'task'; row.dataset.id = t.id;
    var opts = '<option value="">Personne</option>' + NAMES.map(function(n){ return '<option>'+n+'</option>'; }).join('');
    row.innerHTML =
      '<input type="checkbox" id="td-'+t.id+'">' +
      '<div class="t"><label for="td-'+t.id+'"><b>'+t.t+'</b></label><small>'+t.d+'</small><span class="by"></span></div>' +
      '<div class="side"><span class="prio'+(t.now?' now':'')+'">'+t.when+'</span>' +
      '<select id="who-'+t.id+'" aria-label="Qui s’occupe de : '+t.t+'">'+opts+'</select></div>';
    var cb = row.querySelector('input'), sel = row.querySelector('select');
    cb.addEventListener('change', function(){
      if (!me) { cb.checked = !cb.checked; needName(); return; }
      update(t.id, {done: cb.checked});
    });
    sel.addEventListener('change', function(){
      if (!me) { sel.value = (state[t.id] && state[t.id].who) || ''; needName(); return; }
      update(t.id, {who: sel.value});
    });
    host.appendChild(row);
  });

  function needName(){
    say('Choisis d’abord ton prénom en haut de la liste.', true);
    meSel.focus();
  }

  function render(){
    var done = 0, cnt = 0;
    TASKS.forEach(function(t){
      var s = state[t.id] || {}, row = host.querySelector('[data-id="'+t.id+'"]');
      row.querySelector('input').checked = !!s.done;
      var sel = row.querySelector('select'); if (document.activeElement !== sel) sel.value = s.who || '';
      row.classList.toggle('done', !!s.done);
      row.classList.toggle('mine', !!me && s.who === me);
      row.querySelector('.by').textContent = s.done ? 'Fait · coché par ' + s.doneBy + ', ' + when(s.doneAt) : (s.who ? '' : 'Personne pour l’instant');
      var show = filter === 'all' || (filter === 'mine' && me && s.who === me) || (filter === 'free' && !s.who && !s.done);
      row.hidden = !show; if (show) cnt++;
      if (s.done) done++;
    });
    document.getElementById('prog-n').textContent = done + ' / ' + TASKS.length + ' fait';
    document.getElementById('prog-bar').style.width = (done / TASKS.length * 100) + '%';
    document.querySelectorAll('#reserver [data-f]').forEach(function(b){ b.setAttribute('aria-pressed', b.dataset.f === filter); });
    var empty = host.querySelector('.empty');
    if (!cnt) {
      if (!empty) { empty = document.createElement('p'); empty.className = 'empty'; host.appendChild(empty); }
      empty.textContent = filter === 'mine' ? (me ? 'Aucune tâche à ton nom. Prends-en une dans « À attribuer ».' : 'Choisis ton prénom pour voir ta liste.') : 'Tout est attribué.';
    } else if (empty) empty.remove();
  }

  function update(id, patch){
    var prev = JSON.parse(JSON.stringify(state[id] || {}));
    var s = state[id] = Object.assign({}, state[id], patch);
    if ('done' in patch) { s.doneBy = patch.done ? me : ''; s.doneAt = patch.done ? new Date().toISOString() : ''; }
    render();
    if (!shared) { lsSet('gr-todo-local', state); return; }
    fetch(API, {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(Object.assign({id:id, by:me}, patch))})
      .then(function(r){ if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(data){ state = data; say(''); render(); })
      .catch(function(){ state[id] = prev; render(); say('La modification n’a pas été enregistrée. Vérifie ta connexion et réessaie.', true); });
  }

  function load(){
    return fetch(API, {cache:'no-store'})
      .then(function(r){ if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function(data){ shared = true; state = data || {}; render(); });
  }

  meSel.addEventListener('change', function(){ me = meSel.value; lsSet('gr-me', me); say(''); render(); });
  document.querySelectorAll('#reserver [data-f]').forEach(function(b){
    b.addEventListener('click', function(){ filter = b.dataset.f; lsSet('gr-filter', filter); render(); });
  });

  render();
  load().then(function(){
    setInterval(function(){ if (!document.hidden && document.activeElement.tagName !== 'SELECT') load().catch(function(){}); }, 15000);
    document.addEventListener('visibilitychange', function(){ if (!document.hidden) load().catch(function(){}); });
  }).catch(function(){
    shared = false; state = lsGet('gr-todo-local', {}) || {}; render();
    say('Aperçu hors ligne : ici, les coches restent sur cet appareil. La liste partagée fonctionne sur le site du groupe.');
  });

  // Valise : coches personnelles, sur l'appareil uniquement.
  var pack = lsGet('gr-pack', {}) || {};
  document.querySelectorAll('#pack input').forEach(function(cb){
    cb.checked = !!pack[cb.id];
    cb.addEventListener('change', function(){ pack[cb.id] = cb.checked; lsSet('gr-pack', pack); });
  });
})();
