/* Booking widget — clone of the Exely booking engine flow on diamondseahotel.com/booking.
   Steps: 0 search -> 1 select package -> 2 package details -> 3 guest details + payment -> 4 confirmation.
   Payment is SIMULATED (PayOne not connected). */
(function () {
  var I = window.I18N, C = window.CGP, U = window.CGPUI;
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };
  var esc = U.esc;
  var box = $("#tl");
  if (!box) return;

  var iso = function (d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); };
  var parse = function (s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); };
  var addDays = function (s, n) { var d = parse(s); d.setDate(d.getDate() + n); return iso(d); };
  var nightsBetween = function (a, b) { return Math.round((parse(b) - parse(a)) / 864e5); };
  var usd = function (n) { return "USD " + n.toLocaleString("en-US"); };
  var okDate = function (s) { return /^\d{4}-\d{2}-\d{2}$/.test(s || ""); };

  var qs = new URLSearchParams(location.search);
  var today = iso(new Date());
  var S = {
    step: 0,
    checkin: okDate(qs.get("checkin")) && qs.get("checkin") >= today ? qs.get("checkin") : today,
    checkout: null,
    adults: Math.min(4, Math.max(1, +qs.get("adults") || 2)),
    children: 0,
    promo: (qs.get("promo") || "").slice(0, 20),
    cat: "all",
    pkg: C.byId(qs.get("pkg")) || null,
    form: {}
  };
  S.checkout = okDate(qs.get("checkout")) && qs.get("checkout") > S.checkin ? qs.get("checkout") : addDays(S.checkin, 1);
  if (S.pkg) { S.checkout = addDays(S.checkin, S.pkg.nights); S.step = 2; }
  else if (qs.get("checkin")) S.step = 1;

  var ICON = {
    cal: '<svg viewBox="0 0 24 24"><path d="M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 16H5V9h14v11zM7 11h3v3H7zm4 0h3v3h-3zm4 0h2v3h-2zm-8 4h3v3H7zm4 0h3v3h-3z"/></svg>',
    user: '<svg viewBox="0 0 24 24"><path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm0 2c-3 0-8 1.5-8 4.5V21h16v-2.5C20 15.5 15 14 12 14z"/></svg>',
    plus: '<svg viewBox="0 0 24 24"><path d="M11 5h2v14h-2z"/><path d="M5 11h14v2H5z"/></svg>',
    lock: '<svg viewBox="0 0 24 24" width="14" height="14" fill="#3c6098"><path d="M17 9h-1V7a4 4 0 0 0-8 0v2H7a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-9a2 2 0 0 0-2-2zm-7-2a2 2 0 1 1 4 0v2h-4V7z"/></svg>',
    guests: '<svg viewBox="0 0 24 24"><path d="M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm7 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM9 13c-2.7 0-7 1.3-7 4v2h14v-2c0-2.7-4.3-4-7-4zm7 0c-.3 0-.7 0-1.1.1 1.3.9 2.1 2.2 2.1 3.9v2h5v-2c0-2.7-4.3-4-6-4z"/></svg>',
    moon: '<svg viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 9 9 7 7 0 0 1-9-9z"/></svg>',
    mail: '<svg viewBox="0 0 24 24"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5z"/></svg>',
    back: '<svg viewBox="0 0 24 24"><path d="M10 9V5l-7 7 7 7v-4.1c5 0 8.5 1.6 11 5.1-1-5-4-10-11-11z"/></svg>',
    card: '<svg viewBox="0 0 24 24"><path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>',
    qr: '<svg viewBox="0 0 24 24"><path d="M3 3h8v8H3V3zm2 2v4h4V5H5zm8-2h8v8h-8V3zm2 2v4h4V5h-4zM3 13h8v8H3v-8zm2 2v4h4v-4H5zm13-2h3v3h-3v-3zm-5 0h3v3h-3v-3zm3 3h3v3h-3v-3zm-3 3h3v2h-3v-2zm5 0h3v2h-3v-2z"/></svg>'
  };
  var GUESTS = { g1: 1, g2: 2, g12: 2, fam: 4 };

  function bar(pct) { return '<div class="x-hnp__bar"' + (pct ? "" : " hidden") + '><i style="width:' + pct + '%"></i></div>'; }
  function adultsLabel(n) { return I.t("g.a" + n); }
  function guestsLabel() { return adultsLabel(S.adults) + (S.children ? ", " + I.t("tl.c" + S.children) : ""); }
  function rangeLabel() {
    var o = { day: "numeric", month: "long" };
    return I.longDate(parse(S.checkin), o) + " — " + I.longDate(parse(S.checkout), o);
  }

  /* ----- top bar ----- */
  function topBar() {
    var crit = S.step === 0 ? "" :
      '<div class="x-hcp__crit"><button type="button" class="x-scb" data-go="0"><small>' + I.t("tl.cico") + "</small><b>" + esc(rangeLabel()) + '</b></button>' +
      '<button type="button" class="x-scb" data-go="0"><small>' + I.t("box.guests") + "</small><b>" + esc(guestsLabel()) + "</b></button></div>";
    var promo = S.step === 1 || S.step === 2 ? '<button type="button" class="hb" style="background:none;text-transform:none;font-weight:400" data-go="0" data-promo="1">' + ICON.lock + I.t("tl.promoBtn") + "</button>" : "";
    var langs = I.langs.map(function (l) { return '<li><button type="button" data-lang="' + l + '"><img src="' + U.flag(l) + '" alt="">' + esc(window.I18N_NAMES[l]) + "</button></li>"; }).join("");
    return '<div class="x-hcp' + (S.step >= 3 ? " is-locked" : "") + '">' + crit + '<div class="x-hcp__tools">' + promo +
      '<div class="hb-lang"><button type="button" class="hb" data-langmenu aria-label="Language"><img src="' + U.flag(I.lang) + '" alt=""></button><ul>' + langs + "</ul></div>" +
      '<span class="hb">USD</span></div></div>';
  }
  function titleRow(key, backKey, backStep) {
    return '<div class="x-hnp">' + (backKey ? '<button type="button" class="x-hnp__back" data-go="' + backStep + '">' + I.t(backKey) + "</button>" : "") + "<h1>" + I.t(key) + "</h1></div>";
  }

  /* ----- step 0: details of your stay ----- */
  function step0() {
    var ad = [1, 2, 3, 4].map(function (n) { return '<option value="' + n + '"' + (n === S.adults ? " selected" : "") + ">" + adultsLabel(n) + "</option>"; }).join("");
    var ch = '<option value="0">' + I.t("tl.child") + "</option>" + [1, 2].map(function (n) { return '<option value="' + n + '"' + (n === S.children ? " selected" : "") + ">" + I.t("tl.c" + n) + "</option>"; }).join("");
    return topBar() + titleRow("tl.details") + bar(0) +
      '<form class="tl-body" id="f-search" novalidate><div class="psf">' +
      '<div class="psf-row"><label><span class="psf-label">' + I.t("tl.ci") + '</span><span class="x-input"><output data-for="s-ci">' + esc(I.longDate(parse(S.checkin))) + '</output><input class="x-native" type="date" id="s-ci" min="' + today + '" value="' + S.checkin + '" required>' + ICON.cal.replace("<svg", '<svg class="ico-r"') + "</span></label>" +
      '<label><span class="psf-label">' + I.t("tl.co") + '</span><span class="x-input"><output data-for="s-co">' + esc(I.longDate(parse(S.checkout))) + '</output><input class="x-native" type="date" id="s-co" min="' + addDays(S.checkin, 1) + '" value="' + S.checkout + '" required>' + ICON.cal.replace("<svg", '<svg class="ico-r"') + "</span></label></div>" +
      "<hr>" + '<span class="psf-label">' + I.t("tl.stay") + '</span><p class="psf-note">' + I.t("tl.aged") + "</p>" +
      '<div class="psf-row"><label class="x-input has-icon">' + ICON.user.replace("<svg", '<svg class="ico-l"') + '<select id="s-ad">' + ad + '</select><i class="chev"></i></label>' +
      '<label class="x-input has-icon">' + ICON.plus.replace("<svg", '<svg class="ico-l"') + '<select id="s-ch">' + ch + '</select><i class="chev"></i></label></div>' +
      '<p style="margin-top:24px"><button type="button" class="psf-extra" data-extra>' + I.t("tl.extra") + ICON.plus + '</button></p><p class="psf-note" id="s-extra" hidden>' + I.t("tl.extraNote") + "</p>" +
      "<hr>" + '<label class="x-check"><input type="checkbox" id="s-hp"' + (S.promo ? " checked" : "") + "><span>" + I.t("tl.promo") + "</span></label>" +
      '<label class="x-input psf-promo"' + (S.promo ? "" : " hidden") + '><input type="text" id="s-promo" maxlength="20" value="' + esc(S.promo) + '" placeholder="' + I.t("tl.promoBtn") + '" autocomplete="off"></label>' +
      '<button type="submit" class="tl-btn tl-btn--lg">' + I.t("tl.check") + '</button><p class="tl-error" id="s-err" hidden></p></div></form>';
  }

  /* ----- step 1: select a package ----- */
  function pkgCard(p) {
    var best = p.id === 6;
    return '<article class="rcard" data-card="' + p.id + '"><div class="rcard-img"><img src="' + U.img(p.img) + '" alt="' + esc(I.pick(p.names)) + '" loading="lazy" width="660" height="440">' + (best ? '<span class="rcard-badge">🏆 ' + I.t("tl.best1") + "</span>" : "") + "</div>" +
      '<div class="rcard-body"><div class="rcard-name"><h3>' + esc(I.pick(p.names)) + '</h3><button type="button" class="round-btn" data-expand aria-label="+"></button></div>' +
      '<div class="rcard-meta"><span>' + ICON.guests + esc(I.fmt("tl.upto", { n: GUESTS[p.g] })) + "</span><span>" + ICON.moon + esc(I.nights(p.nights)) + "</span></div>" +
      '<p class="rcard-tag">' + esc(I.pick(p.tag)) + '</p><ul class="rcard-more">' + p.inc.map(function (k) { return "<li>" + esc(C.incText(k, p, I)) + "</li>"; }).join("") + "</ul>" +
      '<div class="rcard-price"><small>' + I.t("tl.from") + " </small><b>" + usd(p.price) + "</b><em>" + esc(I.nights(p.nights) + " / " + I.t("gl." + p.g)) + "</em></div>" +
      '<button type="button" class="tl-btn" data-pick="' + p.id + '">' + I.t("tl.sel") + "</button></div></article>";
  }
  function step1() {
    var cats = ["all", "relax", "romance", "family", "long", "sig", "solo"].map(function (c) { return '<button type="button" class="chip' + (S.cat === c ? " is-active" : "") + '" data-cat="' + c + '">' + I.t("cat." + c) + "</button>"; }).join("");
    var list = C.P.filter(function (p) { return S.cat === "all" || p.cat === S.cat; });
    var want = S.adults + S.children;
    list.sort(function (a, b) { return (GUESTS[a.g] >= want ? 0 : 1) - (GUESTS[b.g] >= want ? 0 : 1); });
    var minPrice = Math.min.apply(null, C.P.map(function (p) { return p.price; }));
    var cards = list.map(pkgCard);
    var near = '<aside class="near"><h6>' + I.t("tl.near") + "</h6><ul><li>" + I.t("tl.n1") + "</li><li>" + I.t("tl.n2") + "</li><li>" + I.t("tl.n3") + "</li></ul>" +
      "<h6>" + I.t("tl.top") + "</h6><ul>" + ["am1", "am7", "tile1.t", "am3", "am6", "am8"].map(function (k) { return "<li>" + I.t(k) + "</li>"; }).join("") + "</ul></aside>";
    cards.splice(Math.min(2, cards.length), 0, near);
    return topBar() + titleRow("tl.select") + bar(20) +
      '<div class="tl-body"><div class="x-bpg"><div class="x-bpg__label">' + I.t("tl.best") + '</div><div class="x-bpg__items"><span><i></i>' + I.t("tl.b1") + "</span><span><i></i>" + I.t("tl.b2") + "</span><span><i></i>" + I.t("tl.b3") + "</span></div>" +
      '<div class="x-bpg__price"><small>' + I.t("tl.ourbest") + "</small><b>" + usd(minPrice) + "</b></div></div>" +
      '<div class="filters">' + cats + '</div><div class="rooms-grid-tl">' + cards.join("") + "</div></div>";
  }

  /* ----- step 2: package details (rate plan) ----- */
  function step2() {
    var p = S.pkg, n = nightsBetween(S.checkin, S.checkout);
    var chips = p.inc.slice(0, 4).map(function (k) { return "<span>" + esc(C.incText(k, p, I)) + "</span>"; }).join("") + (p.inc.length > 4 ? "<span>+ " + (p.inc.length - 4) + "</span>" : "");
    var terms = [1, 2, 3, 4, 5, 6, 7, 8].map(function (k) { return "<li>• " + I.t("terms." + k) + "</li>"; }).join("");
    return topBar() + titleRow("tl.rate", "tl.backRooms", 1) + bar(48) +
      '<div class="tl-body"><div class="rp-room"><img src="' + U.img(p.img) + '" alt=""><div><h3>' + esc(I.pick(p.names)) + '</h3><div class="rp-meta"><span>' + esc(I.fmt("tl.upto", { n: GUESTS[p.g] })) + "</span><span>" + esc(I.nights(p.nights)) + "</span><span>" + esc(I.pick(p.badge)) + '</span></div><div class="rp-amen">' + chips + "</div></div><span></span></div>" +
      '<div class="rate"><div><h4>' + esc(I.pick(p.tag)) + '</h4><p class="rate-desc">' + esc(I.pick(p.desc)) + '</p><ul class="rate-list">' + p.inc.map(function (k) { return "<li>" + esc(C.incText(k, p, I)) + "</li>"; }).join("") + "</ul>" +
      '<p class="rate-terms">' + I.t("note.star") + "</p></div>" +
      '<div class="rate-side"><small>' + esc(I.fmt("tl.priceFor", { n: I.nights(p.nights) })) + '</small><div class="row"><b>' + usd(p.price) + '</b><button type="button" class="tl-btn" data-go="3">' + I.t("tl.sel") + "</button></div>" +
      (n !== p.nights ? '<p class="rate-terms">' + esc(I.fmt("tl.minStay", { n: I.nights(p.nights) })) + "<br>" + esc(rangeLabel()) + "</p>" : "") + "</div></div>" +
      '<ul class="rate-terms">' + terms + "</ul></div>";
  }

  /* ----- step 3: enter your details ----- */
  function field(id, key, type, icon) {
    var v = S.form[id] || "";
    return '<label class="x-input' + (icon ? " has-icon" : "") + '">' + (icon ? icon.replace("<svg", '<svg class="ico-l"') : "") + '<input type="' + type + '" id="' + id + '" placeholder="' + I.t(key) + '" value="' + esc(v) + '"' + (icon ? ' style="padding-left:40px"' : "") + "></label>";
  }
  function mybk() {
    var p = S.pkg, ci = parse(S.checkin), co = parse(S.checkout);
    var day = function (d) { return d.toLocaleDateString(["vi-VN", "en-GB", "ko-KR", "zh-CN", "ru-RU", "de-DE"][I.idx], { weekday: "long" }); };
    var mon = function (d) { return I.longDate(d, { month: "long" }); };
    return '<aside class="mybk"><h2>' + I.t("tl.mybk") + '</h2><div class="mybk-n">' + esc(I.nights(p.nights)) + "</div>" +
      '<div class="mybk-dates"><div><i>' + ci.getDate() + "</i> <span>" + esc(mon(ci)) + "</span><em>" + esc(day(ci)) + "</em><small>" + I.t("tl.fromT") + '</small></div><span class="mybk-sep">—</span>' +
      "<div><i>" + co.getDate() + "</i> <span>" + esc(mon(co)) + "</span><em>" + esc(day(co)) + "</em><small>" + I.t("tl.tillT") + "</small></div></div>" +
      '<div class="mybk-room"><div class="row"><b>' + I.t("tl.pkg") + "</b><b>" + usd(p.price) + '</b></div><a href="#" data-go="2">' + esc(I.pick(p.names)) + "</a></div>" +
      '<div class="mybk-lines"><div class="row"><strong>' + esc(guestsLabel()) + '</strong></div><div class="row"><span>' + esc(I.pick(p.badge)) + "</span><span>" + usd(p.price) + "</span></div>" +
      '<div class="row"><strong>' + I.t("tl.svc") + '</strong></div><div class="row"><span>' + I.t("am1") + "</span><span>" + I.t("tl.incl") + "</span></div>" +
      (S.promo ? '<div class="row"><span>' + I.t("sum.promo") + "</span><span>" + esc(S.promo) + "</span></div>" : "") + "</div>" +
      '<div class="mybk-total"><div class="row"><strong>' + I.t("tl.total") + "</strong><b>" + usd(p.price) + '</b></div><hr><div class="row"><strong>' + I.t("tl.paynow") + "</strong><b>" + usd(p.price) + "</b></div>" +
      '<button type="button" class="tl-btn" id="b-book">' + I.t("pay.btn") + '</button><p class="tl-error" id="d-err" hidden></p></div>' +
      '<div class="mybk-foot">' + I.t("tl.summary") + "</div></aside>";
  }
  function step3() {
    var pay = S.form.pay || "card";
    var opt = function (v, key, desc, ico) { return '<label class="pay-opt"><input type="radio" name="pay" value="' + v + '"' + (pay === v ? " checked" : "") + "><strong>" + ico + I.t(key) + "</strong><p>" + I.t(desc) + "</p></label>"; };
    return topBar() + titleRow("tl.enter", "tl.backRate", 2) + bar(80) +
      '<div class="tl-body"><div class="details"><div>' +
      '<section class="plate"><h2 class="plate-cap">' + I.t("tl.customer") + '</h2><div class="plate-body">' +
      "<div>" + I.t("tl.bookfor") + '<span class="seg"><label><input type="radio" name="for" value="me"' + (S.form.for !== "else" ? " checked" : "") + ">" + I.t("tl.me") + '</label><label><input type="radio" name="for" value="else"' + (S.form.for === "else" ? " checked" : "") + ">" + I.t("tl.else") + "</label></span></div>" +
      '<p class="small-note">' + I.t("tl.primary") + "</p><hr>" +
      '<div class="f-grid">' + field("d-first", "tl.first", "text") + field("d-last", "tl.last", "text") +
      field("d-phone", "fm.phone", "tel", '<svg viewBox="0 0 24 24"><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>') +
      field("d-email", "c.email", "email", ICON.mail) + "</div>" +
      '<div class="f-country"><span>' + I.t("fm.country") + "</span>" + field("d-country", "fm.country", "text") + "</div>" +
      '<div class="consents"><p class="info">' + ICON.mail + I.t("tl.conf") + "</p>" +
      '<label class="x-check"><input type="checkbox" id="d-news"' + (S.form.news ? " checked" : "") + "><span>" + I.t("tl.cons1") + "</span></label>" +
      '<label class="x-check" id="d-agree-l"><input type="checkbox" id="d-agree"' + (S.form.agree ? " checked" : "") + "><span>" + I.t("tl.cons2").replace(I.t("f.terms"), '<a href="#terms">' + I.t("f.terms") + "</a>") + "</span></label></div></div></section>" +
      '<section class="plate"><h2 class="plate-cap">' + I.t("tl.add") + '</h2><div class="plate-body"><h4 class="h4">' + I.t("tl.times") + "</h4>" +
      '<div class="times"><span class="x-input"><small>' + I.t("box.checkin") + "</small><b>14:00 — <em>" + I.t("tl.free") + '</em></b></span><span class="x-input is-disabled"><small>' + I.t("box.checkout") + "</small><b>12:00</b></span></div>" +
      '<hr><h4 class="h4">' + I.t("tl.req") + '</h4><textarea class="x-textarea" id="d-note" placeholder="' + I.t("tl.reqph") + '">' + esc(S.form["d-note"] || "") + "</textarea></div></section>" +
      '<section class="plate"><h2 class="plate-cap">' + I.t("tl.paym") + '</h2><div class="plate-body"><p class="pay-info">' + ICON.back + I.t("tl.payinfo") + "</p>" +
      opt("card", "pay.card", "tl.payCardD", ICON.card) + opt("atm", "pay.atm", "tl.payAtmD", ICON.card) + opt("qr", "pay.qr", "tl.payQrD", ICON.qr) +
      '<p class="pay-demo">' + I.t("pay.demo") + "</p></div></section>" +
      "</div>" + mybk() + "</div></div>";
  }

  /* ----- step 4: confirmation ----- */
  function step4() {
    return topBar() + titleRow("ok.title") + bar(100) +
      '<div class="tl-body"><div class="done"><div class="done-ico"></div><h2>' + I.t("ok.title") + "</h2><p>" + I.t("ok.text") + '</p><div class="done-code">' + I.t("ok.code") + "<b>" + esc(S.code) + "</b></div>" +
      "<p>" + esc(I.pick(S.pkg.names)) + " · " + esc(rangeLabel()) + " · " + usd(S.pkg.price) + '</p><p style="margin-top:24px"><a class="tl-btn" style="text-decoration:none" href="' + U.base + '">' + I.t("ok.home") + "</a></p></div></div>";
  }

  /* ----- render + events ----- */
  function save() {
    $$("#tl input[id^='d-'], #tl textarea").forEach(function (el) { S.form[el.id] = el.type === "checkbox" ? el.checked : el.value; });
    if (S.form["d-agree"] !== undefined) S.form.agree = S.form["d-agree"];
    if (S.form["d-news"] !== undefined) S.form.news = S.form["d-news"];
    var f = $("#tl input[name='for']:checked"); if (f) S.form.for = f.value;
    var p = $("#tl input[name='pay']:checked"); if (p) S.form.pay = p.value;
  }
  function render(scroll) {
    box.innerHTML = [step0, step1, step2, step3, step4][S.step]() + '<p class="tl-copy">© CGP Luxury Hotel Booking Engine (demo)</p>';
    var mb = $(".mybk", box);
    if (mb) { var fit = function () { if (!document.body.contains(mb)) return window.removeEventListener("resize", fit); mb.style.top = Math.min(124, window.innerHeight - mb.offsetHeight - 20) + "px"; }; fit(); window.addEventListener("resize", fit); }
    if (scroll) window.scrollTo({ top: box.getBoundingClientRect().top + window.scrollY - 140, behavior: "smooth" });
  }
  function go(n) {
    if (S.step === 3) save();
    if (n >= 2 && !S.pkg) n = 1;
    S.step = n; render(true);
  }

  box.addEventListener("click", function (e) {
    var t = e.target;
    var lm = t.closest("[data-langmenu]");
    if (lm) { lm.parentNode.classList.toggle("is-open"); return; }
    var g = t.closest("[data-go]");
    if (g) { e.preventDefault(); if (g.dataset.promo) S.promo = S.promo || " "; go(+g.dataset.go); if (g.dataset.promo) { S.promo = S.promo.trim(); var hp = $("#s-hp"); if (hp) { hp.checked = true; $(".psf-promo").hidden = false; $("#s-promo").focus(); } } return; }
    var c = t.closest("[data-cat]");
    if (c) { S.cat = c.dataset.cat; render(false); return; }
    if (t.closest("[data-extra]")) { $("#s-extra").hidden = !$("#s-extra").hidden; return; }
    var nat = t.closest(".x-native"); if (nat) { try { nat.showPicker(); } catch (er) {} }
    var x = t.closest("[data-expand]");
    if (x) { x.closest(".rcard").classList.toggle("is-open"); return; }
    var p = t.closest("[data-pick]");
    if (p) { S.pkg = C.byId(p.dataset.pick); S.checkout = addDays(S.checkin, S.pkg.nights); go(2); return; }
    if (t.closest("#b-book")) { submit(); }
  });
  box.addEventListener("change", function (e) {
    var t = e.target;
    if (t.id === "s-hp") { $(".psf-promo").hidden = !t.checked; if (t.checked) $("#s-promo").focus(); }
    if (t.id === "s-ci" && t.value) { var co = $("#s-co"); co.min = addDays(t.value, 1); if (!co.value || co.value <= t.value) co.value = co.min; }
    if (t.id === "s-ci" || t.id === "s-co") $$("#tl output[data-for]").forEach(function (o) { var v = $("#" + o.dataset.for).value; o.textContent = okDate(v) ? I.longDate(parse(v)) : ""; });
  });
  box.addEventListener("submit", function (e) {
    if (e.target.id !== "f-search") return;
    e.preventDefault();
    var ci = $("#s-ci").value, co = $("#s-co").value, err = $("#s-err");
    if (!okDate(ci) || ci < today || !okDate(co) || co <= ci) { err.textContent = I.t("tl.dates"); err.hidden = false; return; }
    S.checkin = ci; S.checkout = co; S.adults = +$("#s-ad").value; S.children = +$("#s-ch").value;
    S.promo = $("#s-hp").checked ? $("#s-promo").value.trim().slice(0, 20) : "";
    go(1);
  });

  function submit() {
    save();
    var ok = true;
    var rules = { "d-first": /\S/, "d-last": /\S/, "d-phone": /^[+\d][\d\s().-]{6,}$/, "d-email": /^[^\s@]+@[^\s@]+\.[^\s@]+$/ };
    Object.keys(rules).forEach(function (id) {
      var el = $("#" + id), good = rules[id].test((el.value || "").trim());
      el.parentNode.classList.toggle("is-invalid", !good); if (!good) ok = false;
    });
    var ag = $("#d-agree");
    $("#d-agree-l").classList.toggle("is-invalid", !ag.checked); if (!ag.checked) ok = false;
    var err = $("#d-err"); err.textContent = I.t("tl.invalid"); err.hidden = ok;
    if (!ok) return;
    /* Demo only: stands in for the redirect to the PayOne hosted payment page. */
    var gw = $("#gateway"); gw.hidden = false;
    setTimeout(function () {
      gw.hidden = true;
      S.code = "CGP-" + Math.random().toString(36).slice(2, 8).toUpperCase();
      S.form = {};
      go(4);
    }, 1800);
  }

  document.addEventListener("langchange", function () { if (S.step === 3) save(); render(false); });
  render(false);
  if (location.hash === "#terms") S.step = S.step;
})();
