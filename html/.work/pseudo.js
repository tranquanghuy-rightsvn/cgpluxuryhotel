(async () => {
  const P = ["content","display","position","top","left","right","bottom","width","height","backgroundColor","backgroundImage","borderTop","borderBottom","opacity","zIndex","boxShadow","transition"];
  const pick = (cs) => { const o = {}; P.forEach((p) => { const v = cs[p]; if (v && !/^(none|normal|auto|0px|rgba\(0, 0, 0, 0\)|static)$/.test(v)) o[p] = v; }); return o; };
  const out = {};
  const sels = ["header.mainHeader", "header.mainHeader .port", ".btLogoArea", ".banner-slider", ".site-slider", ".btSiteFooterWidgets", ".btSiteFooterWidgets .port", "body", ".btPageWrap", "#be-search-form"];
  sels.forEach((s) => { const e = document.querySelector(s); if (!e) return; out[s] = { self: pick(getComputedStyle(e)), before: pick(getComputedStyle(e, "::before")), after: pick(getComputedStyle(e, "::after")), cls: e.className }; });
  scrollTo(0, 900); await new Promise((r) => setTimeout(r, 1500));
  const h = document.querySelector("header.mainHeader");
  out.scrolled = { cls: h.className, self: pick(getComputedStyle(h)), before: pick(getComputedStyle(h, "::before")), after: pick(getComputedStyle(h, "::after")), port: pick(getComputedStyle(h.querySelector(".port"), "::before")), logo: [...h.querySelectorAll(".logo img")].map((i) => i.src + " " + getComputedStyle(i).display + " " + i.getBoundingClientRect().height), a: getComputedStyle(h.querySelector(".mn-home")).color, aMargin: getComputedStyle(h.querySelector(".mn-home")).marginTop, rect: h.getBoundingClientRect().height, bodyCls: document.body.className };
  scrollTo(0, 0);
  return JSON.stringify(out, null, 1);
})()
