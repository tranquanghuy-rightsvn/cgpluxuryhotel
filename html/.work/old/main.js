/* Shared behaviour: header, language switcher, sliders, package cards, modal, news */
(function () {
  var I = window.I18N, C = window.CGP;
  var root = document.body.dataset.root || "./";
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var money = function (n) { return "USD " + n.toLocaleString("en-US"); };
  var img = function (name) { return root + "images/" + name + ".jpg"; };
  var bookUrl = function (id) { return root + "dat-phong/?pkg=" + id; };

  /* ---------- Header ---------- */
  var header = $(".site-header");
  if (header && !document.body.classList.contains("page-sub")) {
    var onScroll = function () { header.classList.toggle("is-solid", window.scrollY > 40); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
  var toggle = $(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open);
    });
    $$(".nav a").forEach(function (a) { a.addEventListener("click", function () { document.body.classList.remove("nav-open"); }); });
  }

  /* ---------- Language switcher ---------- */
  var lang = $(".lang");
  function syncLang() {
    $$(".lang-menu button").forEach(function (b) { b.classList.toggle("is-active", b.dataset.lang === I.lang); });
    var cur = $(".lang-btn span");
    if (cur) cur.textContent = I.lang.toUpperCase();
  }
  if (lang) {
    $(".lang-btn", lang).addEventListener("click", function (e) { e.stopPropagation(); lang.classList.toggle("is-open"); });
    $$(".lang-menu button", lang).forEach(function (b) {
      b.addEventListener("click", function () { I.set(b.dataset.lang); lang.classList.remove("is-open"); });
    });
    document.addEventListener("click", function () { lang.classList.remove("is-open"); });
  }

  /* ---------- Fade slider (hero, intro) ---------- */
  function fadeSlider(box, itemSel, auto) {
    var items = $$(itemSel, box), dots = $(".dots", box), i = 0, timer;
    if (items.length < 2) return;
    function go(n) {
      i = (n + items.length) % items.length;
      items.forEach(function (el, k) { el.classList.toggle("is-active", k === i); });
      if (dots) $$("button", dots).forEach(function (d, k) { d.classList.toggle("is-active", k === i); });
      if (auto) { clearInterval(timer); timer = setInterval(function () { go(i + 1); }, auto); }
    }
    if (dots) {
      dots.innerHTML = items.map(function (_, k) { return '<button type="button" aria-label="Slide ' + (k + 1) + '"></button>'; }).join("");
      $$("button", dots).forEach(function (d, k) { d.addEventListener("click", function () { go(k); }); });
    }
    var prev = $(".slider-arrow--prev", box), next = $(".slider-arrow--next", box);
    if (prev) prev.addEventListener("click", function () { go(i - 1); });
    if (next) next.addEventListener("click", function () { go(i + 1); });
    go(0);
  }
  $$("[data-fade]").forEach(function (box) { fadeSlider(box, box.dataset.fade, +box.dataset.auto || 0); });

  /* ---------- Scroll-snap carousel ---------- */
  function carousel(box) {
    var track = $(".carousel-track", box), dots = box.nextElementSibling;
    if (!dots || !dots.classList.contains("dots")) dots = null;
    function pages() { return Math.max(1, Math.round(track.scrollWidth / track.clientWidth)); }
    function page() { return Math.round(track.scrollLeft / track.clientWidth); }
    function to(p) { track.scrollTo({ left: p * track.clientWidth, behavior: "smooth" }); }
    function build() {
      if (!dots) return;
      var n = pages();
      dots.innerHTML = n > 1 ? new Array(n + 1).join('<button type="button" aria-label="Page"></button>') : "";
      $$("button", dots).forEach(function (d, k) { d.addEventListener("click", function () { to(k); }); });
      mark();
    }
    function mark() { if (dots) $$("button", dots).forEach(function (d, k) { d.classList.toggle("is-active", k === page()); }); }
    $(".slider-arrow--prev", box).addEventListener("click", function () { to(page() === 0 ? pages() - 1 : page() - 1); });
    $(".slider-arrow--next", box).addEventListener("click", function () { to(page() >= pages() - 1 ? 0 : page() + 1); });
    track.addEventListener("scroll", mark, { passive: true });
    window.addEventListener("resize", build);
    box.rebuild = build;
    build();
  }

  /* ---------- Package cards ---------- */
  function meta(p) { return I.nights(p.nights) + " · " + I.t("gl." + p.g); }
  function cardFeatured(p) {
    return '<article class="card">' +
      '<div class="card-media"><img src="' + img(p.img) + '" alt="' + esc(p.name) + '" loading="lazy" width="660" height="440"><span class="badge">' + esc(I.pick(p.badge)) + "</span></div>" +
      '<div class="card-body"><span class="card-meta">' + meta(p) + '</span><h3 class="card-title">' + esc(p.name) + '</h3><p class="card-text">' + esc(I.pick(p.tag)) + "</p>" +
      '<div class="card-foot"><button type="button" class="btn" data-detail="' + p.id + '">' + I.t("btn.details") + '</button><a class="btn" href="' + bookUrl(p.id) + '">' + I.t("btn.book") + "</a></div></div></article>";
  }
  function cardPlain(p) {
    return '<article class="card card--plain">' +
      '<div class="card-media"><img src="' + img(p.img) + '" alt="' + esc(p.name) + '" loading="lazy" width="660" height="440"></div>' +
      '<div class="card-body"><span class="card-meta">' + meta(p) + '</span><h3 class="card-title">' + esc(p.name) + '</h3><p class="card-text">' + esc(I.pick(p.tag)) + "</p>" +
      '<div class="card-foot"><button type="button" class="btn" data-detail="' + p.id + '">' + I.t("btn.detailsShort") + "</button>" +
      '<div><span class="price-label">' + I.t("price.from") + '</span><span class="price">' + money(p.price) + " <small>" + I.t("u." + p.unit) + "</small></span></div></div></div></article>";
  }

  /* ---------- News cards ---------- */
  function newsCard(n) {
    var href = root + "tin-tuc/#" + n.id;
    return '<article class="card news-card">' +
      '<a class="card-media" href="' + href + '"><img src="' + img(n.img) + '" alt="" loading="lazy" width="660" height="440"></a>' +
      '<div class="card-body"><time class="card-meta" datetime="' + n.date + '">' + I.date(new Date(n.date)) + '</time><h3 class="card-title"><a href="' + href + '">' + esc(I.pick(n.title)) + '</a></h3><p class="card-text">' + esc(I.pick(n.body)) + "</p>" +
      '<div class="card-foot"><a class="btn btn--ghost" href="' + href + '">' + I.t("nw.read") + "</a></div></div></article>";
  }
  function newsFull(n) {
    return '<article class="post" id="' + n.id + '">' +
      '<img src="' + img(n.img) + '" alt="" loading="lazy" width="660" height="440">' +
      '<div><time class="card-meta" datetime="' + n.date + '">' + I.date(new Date(n.date)) + '</time><h2 class="h-lg">' + esc(I.pick(n.title)) + '</h2><p class="lead">' + esc(I.pick(n.body)) + "</p></div></article>";
  }

  /* ---------- Render ---------- */
  var renderers = {
    featured: function (el) { el.innerHTML = el.dataset.ids.split(",").map(function (id) { return cardFeatured(C.byId(id)); }).join(""); },
    grid: function (el) { el.innerHTML = el.dataset.ids.split(",").map(function (id) { return cardPlain(C.byId(id)); }).join(""); },
    news: function (el) { el.innerHTML = C.NEWS.slice(0, +el.dataset.limit || 3).map(newsCard).join(""); },
    "news-full": function (el) { el.innerHTML = C.NEWS.map(newsFull).join(""); }
  };
  function render() {
    $$("[data-render]").forEach(function (el) { var fn = renderers[el.dataset.render]; if (fn) fn(el); });
  }

  /* ---------- Detail modal ---------- */
  var modal;
  function openDetail(id) {
    var p = C.byId(id);
    if (!p) return;
    if (!modal) {
      modal = document.createElement("div");
      modal.className = "modal";
      modal.innerHTML = '<div class="modal-box" role="dialog" aria-modal="true"><button type="button" class="modal-close" aria-label="Close">&times;</button><div class="modal-media"></div><div class="modal-body"></div></div>';
      document.body.appendChild(modal);
      modal.addEventListener("click", function (e) { if (e.target === modal || e.target.classList.contains("modal-close")) closeDetail(); });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeDetail(); });
    }
    $(".modal-media", modal).style.backgroundImage = "url(" + img(p.img) + ")";
    $(".modal-body", modal).innerHTML =
      '<span class="card-meta">' + esc(I.pick(p.badge)) + " · " + meta(p) + '</span><h3 class="h-lg">' + esc(p.name) + '</h3><p class="lead" style="margin-top:10px">' + esc(I.pick(p.tag)) + "</p>" +
      '<p class="eyebrow" style="margin-top:22px">' + I.t("incl") + '</p><ul class="ticks">' + p.inc.map(function (k) { return "<li>" + esc(I.pick(C.INC[k])) + "</li>"; }).join("") + "</ul>" +
      '<p class="price">' + money(p.price) + " <small>" + I.t("u." + p.unit) + '</small></p><p class="fine" style="margin:8px 0 20px">' + I.t("note.star") + "</p>" +
      '<a class="btn btn--block" href="' + bookUrl(p.id) + '">' + I.t("btn.book") + "</a>";
    modal.classList.add("is-open");
  }
  function closeDetail() { if (modal) modal.classList.remove("is-open"); }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-detail]");
    if (b) openDetail(b.dataset.detail);
  });

  /* ---------- Home booking box ---------- */
  var box = $(".book-box");
  if (box) {
    var d = new Date(); d.setDate(d.getDate() + 1);
    var iso = function (x) { return x.getFullYear() + "-" + ("0" + (x.getMonth() + 1)).slice(-2) + "-" + ("0" + x.getDate()).slice(-2); };
    var ci = $('[name="checkin"]', box);
    ci.min = iso(new Date()); ci.value = iso(d);
    var promo = $(".promo-toggle", box), promoField = $(".promo-field", box);
    promo.addEventListener("click", function () { promo.hidden = true; promoField.hidden = false; $("input", promoField).focus(); });
  }

  /* ---------- Init ---------- */
  function init() {
    I.apply();
    syncLang();
    render();
    $$(".carousel").forEach(function (c) { c.rebuild ? c.rebuild() : carousel(c); });
  }
  document.addEventListener("langchange", function () { syncLang(); render(); closeDetail(); $$(".carousel").forEach(function (c) { if (c.rebuild) c.rebuild(); }); });
  init();

  window.CGPUI = { money: money, img: img, esc: esc, meta: meta, openDetail: openDetail };
})();
