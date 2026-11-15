/* Shared behaviour. All text is pre-rendered per language in the HTML (SEO);
   JS only handles interaction: sticky header, menus, sliders, carousels, package modal, news search. */
(function () {
  var I = window.I18N, C = window.CGP;
  var root = document.body.dataset.root || "./";
  var base = document.body.dataset.base || root;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var money = function (n) { return "USD " + n.toLocaleString("en-US"); };
  var img = function (name) { return root + "images/" + name + ".jpg"; };
  var FLAGS = { vi: "vi.png", en: "en.png", ko: "ko.svg", zh: "zh.svg", ru: "ru.svg", de: "de.svg" };
  var flag = function (l) { return root + "images/flags/" + FLAGS[l]; };
  var bookUrl = function (id) { return base + "dat-phong/" + (id ? "?pkg=" + id : ""); };
  window.I18N_NAMES = { vi: "Tiếng Việt", en: "English", ko: "한국어", zh: "中文", ru: "Русский", de: "Deutsch" };

  /* ---------- Sticky header ---------- */
  var header = $(".site-header");
  function onScroll() {
    if (!header) return;
    var on = window.scrollY > 200;
    if (on !== header.classList.contains("is-sticky")) header.classList.toggle("is-sticky", on);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile menu + language menu ---------- */
  var toggle = $(".nav-toggle");
  if (toggle) toggle.addEventListener("click", function () { toggle.setAttribute("aria-expanded", document.body.classList.toggle("nav-open")); });
  document.addEventListener("click", function (e) {
    if (document.body.classList.contains("nav-open") && !e.target.closest(".menu, .nav-toggle")) document.body.classList.remove("nav-open");
    var lb = e.target.closest(".lang-btn");
    $$(".lang").forEach(function (box) { box.classList.toggle("is-open", !!lb && box.contains(lb) && !box.classList.contains("is-open")); });
    var b = e.target.closest("button[data-lang]");
    if (b) I.set(b.dataset.lang);
  });

  /* ---------- Fade slider: banner + intro gallery ---------- */
  function fadeSlider(box) {
    var items = $$(box.dataset.fade, box), dots = $(".dots", box), i = 0, timer, auto = +box.dataset.auto || 0, loop = !!box.dataset.loop;
    if (items.length < 2) return;
    function go(n) {
      i = loop ? (n + items.length) % items.length : Math.max(0, Math.min(items.length - 1, n));
      items.forEach(function (el, k) { el.classList.toggle("is-active", k === i); });
      if (dots) $$("button", dots).forEach(function (d, k) { d.classList.toggle("is-active", k === i); });
      var p = $(".arrow--prev", box), x = $(".arrow--next", box);
      if (p && !loop) { p.classList.toggle("is-disabled", i === 0); x.classList.toggle("is-disabled", i === items.length - 1); }
      if (auto) { clearInterval(timer); timer = setInterval(function () { go(i + 1 >= items.length ? 0 : i + 1); }, auto); }
    }
    if (dots) {
      dots.innerHTML = items.map(function (_, k) { return '<button type="button" aria-label="' + (k + 1) + '"></button>'; }).join("");
      $$("button", dots).forEach(function (d, k) { d.addEventListener("click", function () { go(k); }); });
    }
    $$(".slick-prev, .arrow--prev", box).forEach(function (b) { b.addEventListener("click", function () { go(i - 1); }); });
    $$(".slick-next, .arrow--next", box).forEach(function (b) { b.addEventListener("click", function () { go(i + 1); }); });
    go(0);
  }
  $$("[data-fade]").forEach(fadeSlider);

  /* ---------- Carousel (one card per step) ---------- */
  function carousel(box) {
    var track = $(".carousel-track", box), dots = box.nextElementSibling, i = 0;
    if (!dots || !dots.classList.contains("dots")) dots = null;
    function per() { var w = track.children[0] ? track.children[0].getBoundingClientRect().width : 1; return Math.max(1, Math.round((box.clientWidth + 20) / (w + 20))); }
    function max() { return Math.max(0, track.children.length - per()); }
    function go(n) {
      var m = max();
      i = n < 0 ? m : n > m ? 0 : n;
      var c = track.children[i];
      track.style.transform = "translateX(" + (c ? -c.offsetLeft : 0) + "px)";
      if (dots) $$("button", dots).forEach(function (d, k) { d.classList.toggle("is-active", k === i); });
    }
    function build() {
      var n = max() + 1;
      $$(".arrow", box).forEach(function (a) { a.hidden = n < 2; });
      if (dots) {
        dots.innerHTML = n > 1 ? new Array(n + 1).join('<button type="button" aria-label="slide"></button>') : "";
        $$("button", dots).forEach(function (d, k) { d.addEventListener("click", function () { go(k); }); });
      }
      go(Math.min(i, max()));
    }
    $(".arrow--prev", box).addEventListener("click", function () { go(i - 1); });
    $(".arrow--next", box).addEventListener("click", function () { go(i + 1); });
    var sx = null;
    track.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    track.addEventListener("touchend", function (e) { if (sx === null) return; var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go(i + (dx < 0 ? 1 : -1)); sx = null; });
    window.addEventListener("resize", build);
    build();
  }
  $$(".carousel").forEach(carousel);

  /* ---------- Package detail modal ---------- */
  function meta(p) { return I.nights(p.nights) + " · " + I.t("gl." + p.g); }
  var modal;
  function openDetail(id) {
    var p = C.byId(id); if (!p) return;
    if (!modal) {
      modal = document.createElement("div");
      modal.className = "modal";
      modal.innerHTML = '<div class="modal-box" role="dialog" aria-modal="true"><button type="button" class="modal-close" aria-label="Close">&times;</button><div class="modal-img"></div><div class="modal-body"></div></div>';
      document.body.appendChild(modal);
      modal.addEventListener("click", function (e) { if (e.target === modal || e.target.classList.contains("modal-close")) modal.classList.remove("is-open"); });
      document.addEventListener("keydown", function (e) { if (e.key === "Escape") modal.classList.remove("is-open"); });
    }
    $(".modal-img", modal).style.backgroundImage = "url(" + img(p.img) + ")";
    $(".modal-body", modal).innerHTML = '<span class="post-date">' + esc(I.pick(p.badge)) + "</span>" +
      '<h3 class="room-title">' + esc(I.pick(p.names)) + '</h3><p class="sub-title">' + esc(I.pick(p.tag)) + "</p>" + '<p class="modal-desc">' + esc(I.pick(p.desc)) + "</p>" +
      '<span class="price-from">' + I.t("incl") + '</span><ul class="modal-list">' + p.inc.map(function (k) { return "<li>" + esc(C.incText(k, p, I)) + "</li>"; }).join("") + "</ul>" +
      '<span class="price-from">' + esc(meta(p)) + '</span><span class="price">' + money(p.price) + " " + esc(I.t("u." + p.unit)) + "</span>" +
      '<p class="modal-note">' + I.t("note.star") + '</p><a class="btn" href="' + bookUrl(p.id) + '">' + esc(I.pick(p.cta)) + "</a>";
    modal.classList.add("is-open");
  }
  document.addEventListener("click", function (e) {
    var d = e.target.closest("[data-detail]");
    if (d) { e.preventDefault(); openDetail(d.dataset.detail); }
  });

  /* ---------- Home search form ---------- */
  var sfl = $(".sfl");
  if (sfl) {
    var iso = function (d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); };
    var t = new Date(), t2 = new Date(); t2.setDate(t.getDate() + 1);
    var ci = $('[name="checkin"]', sfl), co = $('[name="checkout"]', sfl);
    ci.min = iso(t); ci.value = iso(t); co.min = iso(t2); co.value = iso(t2);
    var show = function () {
      $$("[data-show]", sfl).forEach(function (o) { var v = $('[name="' + o.dataset.show + '"]', sfl).value.split("-"); o.textContent = v.length === 3 ? v[2] + "/" + v[1] + "/" + v[0] : ""; });
    };
    ci.addEventListener("change", function () {
      var d = new Date(ci.value + "T00:00"); d.setDate(d.getDate() + 1);
      co.min = iso(d); if (co.value < co.min) co.value = co.min; show();
    });
    $$(".sfl-native", sfl).forEach(function (n) {
      n.addEventListener("change", show);
      n.addEventListener("click", function () { try { n.showPicker(); } catch (e) {} });
    });
    show();
    var promo = $(".sfl-promo", sfl);
    promo.addEventListener("click", function () { promo.hidden = true; var i = $(".sfl-promo-input", sfl); i.hidden = false; i.focus(); });
  }

  /* ---------- News search (filters the pre-rendered list) ---------- */
  var list = $(".news-list");
  var q = (new URLSearchParams(location.search).get("s") || "").trim();
  if (list && q) {
    var lq = q.toLowerCase(), hits = 0;
    $$("li.news-item", list).forEach(function (li) { var ok = li.textContent.toLowerCase().indexOf(lq) > -1; li.hidden = !ok; if (ok) hits++; });
    var none = $(".news-none", list); if (none) none.hidden = hits > 0;
    $$(".search-box input").forEach(function (i) { i.value = q; });
  }

  window.CGPUI = { money: money, img: img, esc: esc, meta: meta, flag: flag, base: base, openDetail: openDetail };
})();
