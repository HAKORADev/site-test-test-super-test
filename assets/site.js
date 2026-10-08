/* Salt & Ember — site.js (vanilla, no deps) */
(function () {
  "use strict";
  var PREFIX = (window.__SE_DATA__ && window.__SE_DATA__.prefix) || "";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var INDEX = null;

  function fetchIndex(cb) {
    if (INDEX) return cb(INDEX);
    var xhr = new XMLHttpRequest();
    xhr.open("GET", PREFIX + "assets/search-index.json", true);
    xhr.onload = function () { try { INDEX = JSON.parse(xhr.responseText); cb(INDEX); } catch (e) { cb([]); } };
    xhr.onerror = function () { cb([]); };
    xhr.send();
  }

  /* ---------- header ---------- */
  var header = $("#siteHeader");
  if (header) {
    window.addEventListener("scroll", function () {
      header.classList.toggle("scrolled", window.scrollY > 8);
    }, { passive: true });
  }

  /* ---------- toast ---------- */
  var toastEl = null;
  function toast(msg) {
    if (!toastEl) { toastEl = document.createElement("div"); toastEl.className = "toast"; document.body.appendChild(toastEl); }
    toastEl.textContent = msg;
    requestAnimationFrame(function () { toastEl.classList.add("show"); });
    clearTimeout(toastEl._t);
    toastEl._t = setTimeout(function () { toastEl.classList.remove("show"); }, 2600);
  }

  /* ---------- easter egg: click the pot 3x ---------- */
  var logo = $("#logoLink");
  if (logo) {
    var clicks = 0, timer = null, sizzled = false;
    logo.addEventListener("click", function (e) {
      clicks++;
      clearTimeout(timer);
      timer = setTimeout(function () { clicks = 0; }, 900);
      if (clicks >= 3 && !sizzled) {
        sizzled = true; clicks = 0;
        sizzle();
        toast("the pan is hot. nice clicking. 🔥");
        setTimeout(function () { sizzled = false; }, 8000);
      }
    });
  }
  function sizzle() {
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      var ctx = new AC();
      var len = ctx.sampleRate * 1.4;
      var buf = ctx.createBuffer(1, len, ctx.sampleRate);
      var data = buf.getChannelData(0);
      for (var i = 0; i < len; i++) {
        var t = i / ctx.sampleRate;
        var env = Math.min(1, t * 8) * Math.max(0, 1 - t / 1.4);
        var crackle = (Math.random() * 2 - 1);
        if (Math.random() > 0.94) crackle *= 4;
        data[i] = crackle * env * 0.5;
      }
      var src = ctx.createBufferSource(); src.buffer = buf;
      var filt = ctx.createBiquadFilter(); filt.type = "bandpass"; filt.frequency.value = 4200; filt.Q.value = 0.8;
      var g = ctx.createGain(); g.gain.value = 0.6;
      src.connect(filt); filt.connect(g); g.connect(ctx.destination);
      src.start();
    } catch (e) { /* silent kitchen */ }
  }
  function beep(freq, dur, when, type) {
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      var ctx = beep._ctx || (beep._ctx = new AC());
      var o = ctx.createOscillator(), g = ctx.createGain();
      o.type = type || "sine"; o.frequency.value = freq;
      g.gain.setValueAtTime(0.001, ctx.currentTime + when);
      g.gain.exponentialRampToValueAtTime(0.22, ctx.currentTime + when + 0.02);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + when + dur);
      o.connect(g); g.connect(ctx.destination);
      o.start(ctx.currentTime + when); o.stop(ctx.currentTime + when + dur + 0.05);
    } catch (e) { }
  }

  /* ---------- surprise me ---------- */
  function goSurprise(e) {
    if (e) e.preventDefault();
    fetchIndex(function (idx) {
      if (!idx.length) return;
      var pick = idx[Math.floor(Math.random() * idx.length)];
      window.location.href = PREFIX + "recipe/" + pick.slug + ".html";
    });
  }
  var sb = $("#surpriseBtn"); if (sb) sb.addEventListener("click", goSurprise);
  var hs = $("#heroSurprise"); if (hs) hs.addEventListener("click", goSurprise);
  var ns = $("#nfSurprise"); if (ns) ns.addEventListener("click", goSurprise);

  /* ---------- "/" focuses search ---------- */
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && !/input|textarea/i.test(document.activeElement.tagName)) {
      var inp = $(".nav-search input") || $("#filterInput") || $("#searchInput");
      if (inp) { e.preventDefault(); inp.focus(); }
    }
    if (e.key === "Escape" && lbOpen) closeLB();
  });

  /* ---------- recipes page: filters ---------- */
  var grid = $("#recipeGrid");
  if (grid) {
    var cards = $$(".recipe-card", grid);
    var input = $("#filterInput");
    var countEl = $("#filterCount");
    var clearBtn = $("#filterClear");
    var state = { q: "", genre: null, tag: null, base: null, heat: null, budget: null };
    var params = new URLSearchParams(window.location.search);
    if (params.get("q")) { state.q = params.get("q").toLowerCase(); input.value = params.get("q"); }
    if (params.get("genre")) state.genre = params.get("genre");
    if (params.get("tag")) state.tag = params.get("tag");
    $$(".genre-chip").forEach(function (ch) {
      if (ch.dataset.genre === state.genre) ch.classList.add("on");
      ch.addEventListener("click", function () {
        state.genre = state.genre === ch.dataset.genre ? null : ch.dataset.genre;
        $$(".genre-chip").forEach(function (c) { c.classList.toggle("on", c.dataset.genre === state.genre); });
        apply();
      });
    });
    $$(".tag-chip").forEach(function (ch) {
      if (ch.dataset.tag === state.tag) ch.classList.add("on");
      ch.addEventListener("click", function () {
        state.tag = state.tag === ch.dataset.tag ? null : ch.dataset.tag;
        $$(".tag-chip").forEach(function (c) { c.classList.toggle("on", c.dataset.tag === state.tag); });
        apply();
      });
    });
    [["base"], ["heat"], ["budget"]].forEach(function (kv) {
      var key = kv[0];
      $$(".meta-chip[data-" + key + "]").forEach(function (ch) {
        if (ch.dataset[key] === state[key]) ch.classList.add("on");
        ch.addEventListener("click", function () {
          state[key] = state[key] === ch.dataset[key] ? null : ch.dataset[key];
          $$(".meta-chip[data-" + key + "]").forEach(function (c) { c.classList.toggle("on", c.dataset[key] === state[key]); });
          apply();
        });
      });
    });
    input.addEventListener("input", function () { state.q = input.value.toLowerCase(); apply(); });
    clearBtn.addEventListener("click", function () {
      state = { q: "", genre: null, tag: null, base: null, heat: null, budget: null };
      input.value = ""; $$(".chip.on").forEach(function (c) { c.classList.remove("on"); });
      apply();
    });
    function apply() {
      var shown = 0;
      cards.forEach(function (card) {
        var txt = card.textContent.toLowerCase();
        var ok = (!state.q || txt.indexOf(state.q) > -1) &&
                 (!state.genre || card.dataset.genre === state.genre) &&
                 (!state.tag || ("," + card.dataset.tags + ",").indexOf("," + state.tag + ",") > -1) &&
                 (!state.base || card.dataset.base === state.base) &&
                 (!state.heat || card.dataset.heat === state.heat) &&
                 (!state.budget || card.dataset.budget === state.budget);
        card.style.display = ok ? "" : "none";
        if (ok) shown++;
      });
      countEl.textContent = shown + " of " + cards.length + " recipes";
      clearBtn.hidden = !(state.q || state.genre || state.tag || state.base || state.heat || state.budget);
      var nr = $("#noResults");
      if (nr) nr.hidden = shown > 0;
    }
    apply();
  }

  /* ---------- search page ---------- */
  var sInput = $("#searchInput");
  if (sInput) {
    var resBox = $("#searchResults");
    var sel = -1, current = [];
    var quick = $$(".genre-chip[data-q]");
    quick.forEach(function (b) { b.addEventListener("click", function () { sInput.value = b.dataset.q; run(); sInput.focus(); }); });
    sInput.addEventListener("input", run);
    sInput.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(sel + 1, current.length - 1); paintSel(); }
      if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(sel - 1, 0); paintSel(); }
      if (e.key === "Enter" && current[sel]) window.location.href = PREFIX + "recipe/" + current[sel].slug + ".html";
    });
    function paintSel() { $$(".sr-item", resBox).forEach(function (el, i) { el.classList.toggle("sel", i === sel); }); }
    function highlight(text, q) {
      var safe = esc(text);
      if (!q) return safe;
      return safe.replace(new RegExp("(" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig"), "<mark>$1</mark>");
    }
    function run() {
      var q = sInput.value.trim().toLowerCase();
      fetchIndex(function (idx) {
        var qlist = q.split(/\s+/).filter(Boolean);
        var scored = [];
        idx.forEach(function (r) {
          var hay = (r.title + " " + r.genre + " " + r.tags.join(" ")).toLowerCase();
          var body = r.text;
          var score = 0;
          qlist.forEach(function (w) {
            if (r.title.toLowerCase().indexOf(w) > -1) score += 40;
            if (r.tags.join(" ").toLowerCase().indexOf(w) > -1) score += 20;
            if (r.genre.toLowerCase().indexOf(w) > -1) score += 15;
            if (hay.indexOf(w) > -1) score += 10;
            if (body.indexOf(w) > -1) score += 6;
          });
          if (score > 0) scored.push({ r: r, s: score });
        });
        scored.sort(function (a, b) { return b.s - a.s; });
        current = scored.map(function (x) { return x.r; });
        sel = -1;
        var params = new URLSearchParams(window.location.search);
        if (params.get("q") && sInput.value === params.get("q")) { history.replaceState(null, "", "search.html"); }
        if (!q) {
          resBox.innerHTML = '<div class="search-empty">Start typing — or hit one of the quick picks above.</div>';
          return;
        }
        if (!current.length) {
          resBox.innerHTML = '<div class="search-empty">Nothing in the pantry for "<b>' + esc(q) + '</b>". Try fewer words, or browse <a href="' + PREFIX + 'recipes.html">all recipes</a>.</div>';
          return;
        }
        resBox.innerHTML = current.slice(0, 12).map(function (r) {
          var firstWord = qlist[0] || "";
          var kick = highlight(r.kicker, firstWord);
          var originLine = r.origin ? '<span>' + esc(r.origin.split(" — ")[0]) + '</span>' : '';
          return '<a class="sr-item" href="' + PREFIX + 'recipe/' + r.slug + '.html">' +
            '<img src="' + PREFIX + esc(r.img) + '" alt="">' +
            '<div><div class="sr-genre">' + esc(r.genre) + '</div><h3>' + highlight(r.title, firstWord) + '</h3>' +
            '<p>' + kick + '</p>' +
            '<div class="sr-meta"><span>⏱ ' + esc(r.time_label) + '</span><span>◆ ' + esc(r.difficulty) + '</span>' + originLine +
            r.tags.slice(0, 3).map(function (t) { return '<span>#' + esc(t) + '</span>'; }).join("") + '</div></div></a>';
        }).join("");
      });
    }
    var qp = new URLSearchParams(window.location.search);
    if (qp.get("q")) { sInput.value = qp.get("q"); }
    run();
  }

  /* ---------- lightbox ---------- */
  var lbOpen = false, lbImgs = [], lbIdx = 0;
  var lb = document.createElement("div");
  lb.className = "lightbox";
  lb.innerHTML = '<button class="lb-close" aria-label="Close">×</button>' +
    '<button class="lb-nav lb-prev" aria-label="Previous">‹</button>' +
    '<button class="lb-nav lb-next" aria-label="Next">›</button>' +
    '<img alt=""><div class="lb-cap"></div>';
  document.body.appendChild(lb);
  var lbImg = $("img", lb), lbCap = $(".lb-cap", lb);
  function showLB(i) {
    lbIdx = (i + lbImgs.length) % lbImgs.length;
    var src = lbImgs[lbIdx];
    lbImg.src = src.src;
    lbCap.textContent = src.getAttribute("alt") || "";
    lb.classList.add("open"); lbOpen = true;
  }
  function closeLB() { lb.classList.remove("open"); lbOpen = false; }
  $(".lb-close", lb).addEventListener("click", closeLB);
  $(".lb-prev", lb).addEventListener("click", function () { showLB(lbIdx - 1); });
  $(".lb-next", lb).addEventListener("click", function () { showLB(lbIdx + 1); });
  lb.addEventListener("click", function (e) { if (e.target === lb) closeLB(); });
  document.addEventListener("keydown", function (e) {
    if (!lbOpen) return;
    if (e.key === "ArrowLeft") showLB(lbIdx - 1);
    if (e.key === "ArrowRight") showLB(lbIdx + 1);
  });
  var galItems = $$(".gal-item");
  if (galItems.length) {
    galItems.forEach(function (fig, i) {
      fig.addEventListener("click", function () {
        lbImgs = $$("img", fig.parentNode);
        showLB(Array.prototype.indexOf.call($$("img", fig.parentNode), $("img", fig)));
      });
    });
  }

  /* ---------- video facades ---------- */
  $$(".video-card").forEach(function (card) {
    function load() {
      if (card.querySelector("iframe")) return;
      var id = card.dataset.yt;
      var wrap = card.querySelector(".video-thumb");
      wrap.outerHTML = '<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/' + esc(id) + '?autoplay=1&rel=0" title="Recipe video" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>';
    }
    card.addEventListener("click", load);
    card.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); load(); } });
  });

  /* ---------- kitchen timer ---------- */
  var tDisp = $("#timerDisplay");
  if (tDisp) {
    var tLeft = 0, tRun = null;
    function fmt(s) { var m = Math.floor(s / 60), ss = s % 60; return (m < 10 ? "0" : "") + m + ":" + (ss < 10 ? "0" : "") + ss; }
    function paint() { tDisp.textContent = fmt(tLeft); }
    function stop() { clearInterval(tRun); tRun = null; tDisp.classList.remove("running", "done"); document.title = document.title.replace(/^⏳ /, ""); }
    function tick() {
      tLeft--;
      if (tLeft <= 0) {
        stop(); tLeft = 0; paint(); tDisp.classList.add("done");
        toast("⏰ timer done — go check the pot!");
        [0, 0.35, 0.7].forEach(function (w, i) { beep(i === 2 ? 1319 : 988, 0.28, w, "square"); });
        return;
      }
      paint();
    }
    $$(".btn[data-timer]").forEach(function (b) {
      b.addEventListener("click", function () {
        stop(); tLeft = parseInt(b.dataset.timer, 10) * 60; paint();
        tDisp.classList.add("running");
        tRun = setInterval(tick, 1000);
      });
    });
    $("#timerSet").addEventListener("click", function () {
      var m = parseInt($("#timerMin").value, 10);
      if (!m || m < 0) return;
      stop(); tLeft = m * 60; paint();
    });
    $("#timerStart").addEventListener("click", function () {
      if (tRun) { stop(); return; }
      if (!tLeft) return;
      tDisp.classList.add("running");
      tRun = setInterval(tick, 1000);
    });
    $("#timerReset").addEventListener("click", function () { stop(); tLeft = 0; paint(); });
  }

  /* ---------- ingredient checkboxes ---------- */
  $$(".ing input[data-ing]").forEach(function (cb) {
    var key = "se-ing-" + cb.dataset.ing;
    var i = Array.prototype.indexOf.call($$(".ing input[data-ing]"), cb);
    var store = JSON.parse(localStorage.getItem(key) || "[]");
    if (store.indexOf(i) > -1) cb.checked = true;
    cb.addEventListener("change", function () {
      var st = JSON.parse(localStorage.getItem(key) || "[]");
      if (cb.checked) { if (st.indexOf(i) === -1) st.push(i); } else { st = st.filter(function (x) { return x !== i; }); }
      localStorage.setItem(key, JSON.stringify(st));
    });
  });

  /* ---------- github issues comments ---------- */
  var gh = $("#ghComments");
  if (gh) {
    var slug = gh.dataset.slug, title = gh.dataset.title, repo = gh.dataset.repo;
    var newBtn = $("#ghNewComment");
    newBtn.href = "https://github.com/" + repo + "/issues/new?labels=recipe%3A" + encodeURIComponent(slug) +
      "&title=" + encodeURIComponent("💬 " + title) +
      "&body=" + encodeURIComponent("Comment from the recipe page: " + location.href + "\n\n");
    var api = "https://api.github.com/repos/" + repo + "/issues?labels=recipe%3A" + encodeURIComponent(slug) + "&state=all";
    var x = new XMLHttpRequest();
    x.open("GET", api, true);
    x.onload = function () {
      if (x.status !== 200) {
        gh.innerHTML = '<div class="comment-loading">GitHub is not answering right now (rate limits happen). You can always <a href="' + esc(newBtn.href) + '" target="_blank" rel="noopener">open an issue directly</a>.</div>';
        return;
      }
      var issues = JSON.parse(x.responseText);
      if (!issues.length) {
        gh.innerHTML = '<div class="comment-count-line">No comments yet — be the first voice in this recipe\'s little black book.</div>';
        return;
      }
      var issue = issues[0];
      gh.innerHTML = '<div class="comment-count-line">' + issue.comments + (issue.comments === 1 ? ' comment' : ' comments') + ' · from GitHub Issues</div><div id="ghBody"><div class="comment-loading">Loading the conversation…</div></div>';
      if (!issue.comments) { $("#ghBody").innerHTML = '<div class="comment-count-line">Issue open, zero comments — the floor is yours.</div>'; return; }
      var xc = new XMLHttpRequest();
      xc.open("GET", "https://api.github.com/repos/" + repo + "/issues/" + issue.number + "/comments", true);
      xc.onload = function () {
        var box = $("#ghBody");
        if (xc.status !== 200) { box.innerHTML = '<div class="comment-loading">Could not load comments (rate limited). Try again later.</div>'; return; }
        var cs = JSON.parse(xc.responseText);
        box.innerHTML = cs.map(function (c) {
          var d = new Date(c.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
          var body = esc(c.body).replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
          return '<div class="comment"><div class="comment-head"><img src="' + esc(c.user.avatar_url) + '&s=64" alt="">' +
            '<div><div class="comment-author">' + esc(c.user.login) + '</div><div class="comment-date">' + d + '</div></div></div>' +
            '<div class="comment-body">' + body + '</div></div>';
        }).join("");
      };
      xc.send();
    };
    x.onerror = function () { gh.innerHTML = '<div class="comment-loading">Comments are offline (network). The recipe still works though.</div>'; };
    x.send();
  }
})();
