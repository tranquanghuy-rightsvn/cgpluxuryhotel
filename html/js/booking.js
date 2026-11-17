/* Booking widget — clone of the Exely booking engine flow on diamondseahotel.com/booking.
   Steps: 0 search -> 1 select package -> 2 package details -> 3 guest details + payment -> 4 confirmation.
   Every step is pre-rendered in the page's language by .work/build.py (SEO, no text in JS).
   This script only switches steps, filters/sorts the cards and fills in the guest's own choices.
   Payment is SIMULATED (PayOne not connected). */
(function () {
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var box = $("#tl");
  if (!box) return;

  var LOCALE = { vi: "vi-VN", en: "en-GB", ko: "ko-KR", zh: "zh-CN", ru: "ru-RU", de: "de-DE" }[document.documentElement.lang] || "vi-VN";
  var iso = function (d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); };
  var parse = function (s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); };
  var addDays = function (s, n) { var d = parse(s); d.setDate(d.getDate() + n); return iso(d); };
  var nightsBetween = function (a, b) { return Math.round((parse(b) - parse(a)) / 864e5); };
  var okDate = function (s) { return /^\d{4}-\d{2}-\d{2}$/.test(s || ""); };
  var dateText = function (s, opt) { return parse(s).toLocaleDateString(LOCALE, opt || { day: "numeric", month: "long", year: "numeric" }); };
  var setText = function (key, v) { $$('[data-v="' + key + '"]', box).forEach(function (el) { el.textContent = v; }); };

  /* package facts come from the pre-rendered step-2 blocks */
  var PK = {};
  $$(".rp-pkg", box).forEach(function (el) { PK[el.dataset.pkg] = { el: el, nights: +el.dataset.nights }; });

  var qs = new URLSearchParams(location.search);
  var today = iso(new Date());
  var S = { step: 0, cat: "all", pkg: PK[qs.get("pkg")] ? qs.get("pkg") : null };
  S.checkin = okDate(qs.get("checkin")) && qs.get("checkin") >= today ? qs.get("checkin") : today;
  S.checkout = okDate(qs.get("checkout")) && qs.get("checkout") > S.checkin ? qs.get("checkout") : addDays(S.checkin, 1);
  if (S.pkg) { S.checkout = addDays(S.checkin, PK[S.pkg].nights); S.step = 2; }
  else if (qs.get("checkin")) S.step = 1;

  /* ----- step 0 form: initial values ----- */
  var ci = $("#s-ci"), co = $("#s-co"), ad = $("#s-ad"), ch = $("#s-ch"), hp = $("#s-hp"), promo = $("#s-promo");
  ad.value = String(Math.min(4, Math.max(1, +qs.get("adults") || 2)));
  promo.value = (qs.get("promo") || "").slice(0, 20);
  hp.checked = !!promo.value;
  $(".psf-promo", box).hidden = !hp.checked;
  function syncDates() {
    ci.min = today; ci.value = S.checkin;
    co.min = addDays(S.checkin, 1); co.value = S.checkout;
    showDates();
  }
  function showDates() { $$("output[data-for]", box).forEach(function (o) { var v = $("#" + o.dataset.for).value; o.textContent = okDate(v) ? dateText(v) : ""; }); }

  /* ----- guest's choices -> placeholders ----- */
  function fill() {
    var o = { day: "numeric", month: "long" };
    setText("range", dateText(S.checkin, o) + " — " + dateText(S.checkout, o));
    setText("guests", ad.options[ad.selectedIndex].text + (+ch.value ? ", " + ch.options[ch.selectedIndex].text : ""));
    var p = S.pkg && PK[S.pkg];
    if (!p) return;
    ["name", "nights", "badge", "price"].forEach(function (k) { setText(k, $('[data-k="' + k + '"]', p.el).textContent); });
    $$(".rp-pkg", box).forEach(function (el) { el.hidden = el !== p.el; });
    $("[data-minstay]", p.el).hidden = nightsBetween(S.checkin, S.checkout) === p.nights;
    [["ci", S.checkin], ["co", S.checkout]].forEach(function (x) {
      var d = parse(x[1]);
      setText(x[0] + "-d", d.getDate());
      setText(x[0] + "-m", d.toLocaleDateString(LOCALE, { month: "long" }));
      setText(x[0] + "-w", d.toLocaleDateString(LOCALE, { weekday: "long" }));
    });
    var pr = promo.value.trim();
    setText("promo", pr);
    $("[data-promo-row]", box).hidden = !(hp.checked && pr);
  }

  /* ----- step 1: filter + sort cards (cards that fit the party first) ----- */
  function arrange() {
    var grid = $(".rooms-grid-tl", box), near = $(".near", grid), want = +ad.value + +ch.value;
    var cards = $$(".rcard", grid);
    cards.sort(function (a, b) { return ((+a.dataset.guests >= want ? 0 : 1) - (+b.dataset.guests >= want ? 0 : 1)) || (a.dataset.card - b.dataset.card); });
    cards.forEach(function (el) { el.hidden = S.cat !== "all" && el.dataset.cat !== S.cat; grid.appendChild(el); });
    var vis = cards.filter(function (el) { return !el.hidden; });
    grid.insertBefore(near, vis[2] || null);
    $$("[data-cat]", $(".filters", box)).forEach(function (b) { b.classList.toggle("is-active", b.dataset.cat === S.cat); });
  }

  /* ----- show a step ----- */
  function show(n, scroll) {
    if (n >= 2 && !S.pkg) n = 1;
    S.step = n;
    $$(".tl-step", box).forEach(function (el) { el.hidden = +el.dataset.step !== n; });
    $$("[data-steps]", box).forEach(function (el) { el.hidden = el.dataset.steps.split(" ").indexOf(String(n)) < 0; });
    $(".x-hcp", box).classList.toggle("is-locked", n >= 3);
    if (n === 1) arrange();
    fill();
    var mb = $(".mybk", box);
    if (n === 3) mb.style.top = Math.min(124, window.innerHeight - mb.offsetHeight - 20) + "px";
    if (scroll) window.scrollTo({ top: box.getBoundingClientRect().top + window.scrollY - 140, behavior: "smooth" });
  }
  window.addEventListener("resize", function () { if (S.step === 3) show(3, false); });

  box.addEventListener("click", function (e) {
    var t = e.target;
    var lm = t.closest("[data-langmenu]");
    if (lm) { lm.parentNode.classList.toggle("is-open"); return; }
    var g = t.closest("[data-go]");
    if (g) {
      e.preventDefault(); show(+g.dataset.go, true);
      if (g.dataset.promo) { hp.checked = true; $(".psf-promo", box).hidden = false; promo.focus(); }
      return;
    }
    var c = t.closest("[data-cat]");
    if (c && c.classList.contains("chip")) { S.cat = c.dataset.cat; arrange(); return; }
    if (t.closest("[data-extra]")) { $("#s-extra").hidden = !$("#s-extra").hidden; return; }
    var nat = t.closest(".x-native"); if (nat) { try { nat.showPicker(); } catch (er) {} }
    var x = t.closest("[data-expand]");
    if (x) { x.closest(".rcard").classList.toggle("is-open"); return; }
    var p = t.closest("[data-pick]");
    if (p) { S.pkg = p.dataset.pick; S.checkout = addDays(S.checkin, PK[S.pkg].nights); syncDates(); show(2, true); return; }
    if (t.closest("#b-book")) submit();
  });
  box.addEventListener("change", function (e) {
    var t = e.target;
    if (t === hp) { $(".psf-promo", box).hidden = !t.checked; if (t.checked) promo.focus(); }
    if (t === ci && t.value) { co.min = addDays(t.value, 1); if (!co.value || co.value <= t.value) co.value = co.min; }
    if (t === ci || t === co) showDates();
  });
  box.addEventListener("submit", function (e) {
    if (e.target.id !== "f-search") return;
    e.preventDefault();
    var err = $("#s-err");
    if (!okDate(ci.value) || ci.value < today || !okDate(co.value) || co.value <= ci.value) { err.hidden = false; return; }
    err.hidden = true;
    S.checkin = ci.value; S.checkout = co.value;
    if (!hp.checked) promo.value = "";
    show(1, true);
  });

  function submit() {
    var ok = true;
    var rules = { "d-first": /\S/, "d-last": /\S/, "d-phone": /^[+\d][\d\s().-]{6,}$/, "d-email": /^[^\s@]+@[^\s@]+\.[^\s@]+$/ };
    Object.keys(rules).forEach(function (id) {
      var el = $("#" + id), good = rules[id].test((el.value || "").trim());
      el.parentNode.classList.toggle("is-invalid", !good); if (!good) ok = false;
    });
    var ag = $("#d-agree");
    $("#d-agree-l").classList.toggle("is-invalid", !ag.checked); if (!ag.checked) ok = false;
    $("#d-err").hidden = ok;
    if (!ok) return;
    /* Demo only: stands in for the redirect to the PayOne hosted payment page. */
    var gw = $("#gateway"); gw.hidden = false;
    setTimeout(function () {
      gw.hidden = true;
      setText("code", "CGP-" + Math.random().toString(36).slice(2, 8).toUpperCase());
      $$(".details input[type=text], .details input[type=tel], .details input[type=email], .details textarea", box).forEach(function (el) { el.value = ""; });
      $$(".details input[type=checkbox]", box).forEach(function (el) { el.checked = false; });
      show(4, true);
    }, 1800);
  }

  syncDates();
  show(S.step, false);
})();
