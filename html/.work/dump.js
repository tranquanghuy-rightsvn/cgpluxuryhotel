(() => {
  const P = ["display","position","top","left","right","bottom","zIndex","width","height","maxWidth","minHeight","marginTop","marginRight","marginBottom","marginLeft","paddingTop","paddingRight","paddingBottom","paddingLeft","flexDirection","justifyContent","alignItems","gap","gridTemplateColumns","float","color","backgroundColor","backgroundImage","backgroundSize","backgroundPosition","fontFamily","fontSize","fontWeight","fontStyle","lineHeight","letterSpacing","textTransform","textAlign","textDecorationLine","borderTop","borderRight","borderBottom","borderLeft","borderRadius","boxShadow","opacity","overflow","objectFit","whiteSpace","transform"];
  const SKIP = /^(SCRIPT|STYLE|NOSCRIPT|LINK|META|svg|path|BR)$/i;
  function node(el, depth, doc) {
    if (SKIP.test(el.tagName)) return null;
    const cs = (doc.defaultView || window).getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return null;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0 && el.children.length === 0) return null;
    const s = {};
    P.forEach((p) => { const v = cs[p]; if (v && v !== "none" && v !== "normal" && v !== "auto" && v !== "0px" && v !== "rgba(0, 0, 0, 0)" && !/^0px none/.test(v) && v !== "static" && v !== "visible" && v !== "start") s[p] = v; });
    const o = { t: el.tagName.toLowerCase() };
    if (el.id) o.id = el.id;
    const c = el.getAttribute("class"); if (c) o.c = c.trim().replace(/\s+/g, " ");
    o.r = [Math.round(r.left), Math.round(r.top + (doc.defaultView || window).scrollY), Math.round(r.width), Math.round(r.height)];
    const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(" ").trim();
    if (own) o.x = own.slice(0, 400);
    if (el.src) o.src = el.currentSrc || el.src;
    if (el.getAttribute("href")) o.href = el.getAttribute("href");
    if (el.placeholder) o.ph = el.placeholder;
    if (el.type && /INPUT|BUTTON/.test(el.tagName)) o.type = el.type;
    if (el.value && /INPUT|SELECT/.test(el.tagName)) o.val = el.value;
    o.s = s;
    if (depth < 22) {
      let kids = [...el.children];
      if (el.tagName === "IFRAME") { try { kids = [el.contentDocument.body]; } catch (e) {} }
      const ch = kids.map((k) => node(k, depth + 1, k.ownerDocument)).filter(Boolean);
      if (ch.length) o.k = ch;
    }
    return o;
  }
  const out = {};
  out.header = node(document.querySelector("header.mainHeader"), 0, document);
  out.sections = [...document.querySelectorAll(".bt_bb_wrapper > section")].map((s) => node(s, 0, document));
  out.footer = node(document.querySelector(".btSiteFooterWidgets") || document.querySelector("footer"), 0, document);
  const ifr = document.querySelector("#be-search-form iframe");
  try { out.bookingDoc = ifr.contentDocument.documentElement.outerHTML.length; } catch (e) { out.bookingDoc = "x-origin"; }
  return JSON.stringify(out);
})()
