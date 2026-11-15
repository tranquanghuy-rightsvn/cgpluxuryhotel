/* Booking flow (client-side demo): select package -> guest details -> PayOne (simulated) -> confirmation */
(function () {
  var I = window.I18N, C = window.CGP, U = window.CGPUI;
  var $ = function (s) { return document.querySelector(s); };
  var $$ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };
  var qs = new URLSearchParams(location.search);
  var iso = function (d) { return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); };
  var parse = function (s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); };

  var tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1);
  var state = {
    step: 1,
    cat: "all",
    pkg: C.byId(qs.get("pkg")) || null,
    checkin: /^\d{4}-\d{2}-\d{2}$/.test(qs.get("checkin") || "") ? qs.get("checkin") : iso(tomorrow)
  };

  var preselected = state.pkg; /* package chosen on another page is listed first */
  var fCheckin = $("#f-checkin"), fNights = $("#f-nights"), fGuests = $("#f-guests"), fPromo = $("#f-promo");
  var list = $("#pkg-list"), sumBody = $("#sum-body"), next = $("#btn-next"), back = $("#btn-back");
  fCheckin.min = iso(new Date());
  if (state.checkin < fCheckin.min) state.checkin = iso(tomorrow);
  fCheckin.value = state.checkin;
  if (!state.pkg) {
    if (["3", "4", "5", "7"].indexOf(qs.get("nights")) > -1) fNights.value = qs.get("nights");
    if (["g1", "g2", "fam"].indexOf(qs.get("guests")) > -1 && qs.get("nights") !== null) fGuests.value = qs.get("guests");
  }
  fPromo.value = (qs.get("promo") || "").slice(0, 20);

  function matches(p) {
    if (state.cat !== "all" && p.cat !== state.cat) return false;
    if (fNights.value && p.nights !== +fNights.value) return false;
    if (fGuests.value && p.g !== fGuests.value && !(p.g === "g12" && fGuests.value !== "fam")) return false;
    return true;
  }

  function renderList() {
    var items = C.P.filter(matches);
    if (preselected && items.indexOf(preselected) > 0) { items.splice(items.indexOf(preselected), 1); items.unshift(preselected); }
    list.innerHTML = items.length ? items.map(function (p) {
      var sel = state.pkg === p;
      return '<article class="pkg-row' + (sel ? " is-selected" : "") + '">' +
        '<div class="card-media"><img src="' + U.img(p.img) + '" alt="' + U.esc(p.name) + '" loading="lazy" width="660" height="440"><span class="badge">' + U.esc(I.pick(p.badge)) + "</span></div>" +
        '<div class="pkg-info"><span class="card-meta">' + U.meta(p) + '</span><h3 class="card-title">' + U.esc(p.name) + '</h3><p class="card-text">' + U.esc(I.pick(p.tag)) + "</p>" +
        '<ul class="ticks">' + p.inc.slice(0, 4).map(function (k) { return "<li>" + U.esc(I.pick(C.INC[k])) + "</li>"; }).join("") + "</ul>" +
        '<button type="button" class="link" data-detail="' + p.id + '">' + I.t("btn.details") + " (" + p.inc.length + ")</button></div>" +
        '<div class="pkg-side"><div><span class="price-label">' + I.t("price.from") + '</span><span class="price">' + U.money(p.price) + "<small>" + I.t("u." + p.unit) + "</small></span></div>" +
        '<button type="button" class="btn' + (sel ? " btn--navy" : "") + '" data-select="' + p.id + '">' + I.t(sel ? "bk.selected" : "bk.select") + "</button></div></article>";
    }).join("") : '<p class="pkg-empty">' + I.t("bk.none") + "</p>";
    $$(".cats button").forEach(function (b) { b.classList.toggle("is-active", b.dataset.cat === state.cat); });
  }

  function renderSummary() {
    var p = state.pkg;
    if (!p) { sumBody.innerHTML = '<p class="sum-empty">' + I.t("sum.empty") + "</p>"; return; }
    var ci = parse(state.checkin), co = new Date(ci); co.setDate(co.getDate() + p.nights);
    sumBody.innerHTML = '<img class="sum-img" src="' + U.img(p.img) + '" alt="">' +
      '<p class="sum-name">' + U.esc(p.name) + "</p>" +
      '<dl class="sum-rows">' +
      "<div><dt>" + I.t("box.checkin") + "</dt><dd>" + I.date(ci) + "</dd></div>" +
      "<div><dt>" + I.t("box.checkout") + "</dt><dd>" + I.date(co) + "</dd></div>" +
      "<div><dt>" + I.t("box.nights") + "</dt><dd>" + I.nights(p.nights) + "</dd></div>" +
      "<div><dt>" + I.t("sum.guests") + "</dt><dd>" + I.t("gl." + p.g) + "</dd></div></dl>" +
      '<p class="sum-total"><span>' + I.t("sum.total") + '</span><span class="price">' + U.money(p.price) + "</span></p>";
  }

  function showStep(n) {
    state.step = n;
    $$("[data-panel]").forEach(function (el) { el.hidden = +el.dataset.panel !== n; });
    $$(".steps li").forEach(function (li) {
      var s = +li.dataset.step;
      li.classList.toggle("is-active", s === n);
      li.classList.toggle("is-done", s < n);
    });
    back.hidden = n === 1 || n === 4;
    next.hidden = n === 4;
    $("#sum-promo").hidden = n === 4;
    fPromo.disabled = n > 2;
    next.dataset.i18n = n === 3 ? "pay.btn" : "sum.next";
    next.textContent = I.t(next.dataset.i18n);
    if (n > 1) window.scrollTo({ top: $(".steps").getBoundingClientRect().top + window.scrollY - 90, behavior: "smooth" });
  }

  function validGuest() {
    var ok = true;
    [["#g-name", /\S{2,}/], ["#g-email", /^[^\s@]+@[^\s@]+\.[^\s@]+$/], ["#g-phone", /^[+\d][\d\s().-]{6,}$/]].forEach(function (r) {
      var el = $(r[0]), good = r[1].test(el.value.trim());
      el.classList.toggle("is-invalid", !good);
      if (!good) ok = false;
    });
    $("#form-error").hidden = ok;
    return ok;
  }

  next.addEventListener("click", function () {
    if (state.step === 1) {
      if (!state.pkg) {
        var e = $(".sum-empty"); if (e) e.classList.add("is-invalid");
        return;
      }
      showStep(2);
    } else if (state.step === 2) {
      if (validGuest()) showStep(3);
    } else if (state.step === 3) {
      var agree = $("#agree");
      agree.parentNode.classList.toggle("is-invalid", !agree.checked);
      if (!agree.checked) return;
      /* Demo only: simulates the redirect to the PayOne hosted payment page. */
      var gw = $("#gateway");
      gw.hidden = false;
      setTimeout(function () {
        gw.hidden = true;
        var code = "CGP-" + Math.random().toString(36).slice(2, 8).toUpperCase();
        $("#done-code").textContent = code;
        showStep(4);
      }, 1800);
    }
  });
  back.addEventListener("click", function () { if (state.step > 1 && state.step < 4) showStep(state.step - 1); });
  $('[data-panel="2"]').addEventListener("submit", function (e) { e.preventDefault(); next.click(); });

  list.addEventListener("click", function (e) {
    var b = e.target.closest("[data-select]");
    if (!b) return;
    state.pkg = C.byId(b.dataset.select);
    renderList(); renderSummary();
  });
  $(".cats").addEventListener("click", function (e) {
    var b = e.target.closest("[data-cat]");
    if (b) { state.cat = b.dataset.cat; renderList(); }
  });
  fNights.addEventListener("change", renderList);
  fGuests.addEventListener("change", renderList);
  fCheckin.addEventListener("change", function () {
    if (fCheckin.value && fCheckin.value >= fCheckin.min) state.checkin = fCheckin.value; else fCheckin.value = state.checkin;
    renderSummary();
  });
  document.addEventListener("langchange", function () { renderList(); renderSummary(); next.textContent = I.t(next.dataset.i18n); });

  renderList(); renderSummary(); showStep(1);
  if (location.hash === "#terms") $("#terms").open = true;
})();
