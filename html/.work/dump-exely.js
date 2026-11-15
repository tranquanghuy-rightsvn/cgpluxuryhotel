(() => {
  const f = [...document.querySelectorAll("#be-booking-form iframe")].find((x) => x.getBoundingClientRect().height > 50);
  const d = f.contentDocument;
  const P = ["display","width","height","marginTop","marginBottom","paddingTop","paddingRight","paddingBottom","paddingLeft","color","backgroundColor","backgroundImage","fontFamily","fontSize","fontWeight","lineHeight","letterSpacing","textTransform","textAlign","textDecorationLine","borderTop","borderRight","borderBottom","borderLeft","borderRadius","boxShadow","gap","justifyContent","alignItems","flexDirection","gridTemplateColumns","position","top","left","right","zIndex","opacity"];
  const fr = f.getBoundingClientRect();
  function node(el, dep) {
    if (/^(SCRIPT|STYLE|NOSCRIPT|LINK|META|path|BR)$/i.test(el.tagName)) return null;
    const cs = d.defaultView.getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return null;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) return null;
    const s = {};
    P.forEach((p) => { const v = cs[p]; if (v && !/^(none|normal|auto|0px|rgba\(0, 0, 0, 0\)|static|visible|start)$/.test(v) && !/^0px none/.test(v)) s[p] = v; });
    const o = { t: el.tagName.toLowerCase(), r: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)], s };
    const c = el.getAttribute("class"); if (c) o.c = c.trim().replace(/\s+/g, " ").slice(0, 80);
    const own = [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent.trim()).join(" ").trim();
    if (own) o.x = own.slice(0, 200);
    if (el.placeholder) o.ph = el.placeholder;
    if (el.tagName === "svg") { o.svg = el.outerHTML.slice(0, 1500); return o; }
    if (dep < 40) { const k = [...el.children].map((c) => node(c, dep + 1)).filter(Boolean); if (k.length) o.k = k; }
    return o;
  }
  const fonts = [...d.fonts].filter((x) => x.status === "loaded").map((x) => x.family + " " + x.weight + " " + x.style);
  const faces = [];
  for (const sh of d.styleSheets) { try { for (const r of sh.cssRules) if (r.constructor.name === "CSSFontFaceRule") faces.push(r.cssText.slice(0, 400)); } catch (e) {} }
  return JSON.stringify({ frame: [fr.left, fr.top, fr.width, fr.height], fonts: [...new Set(fonts)], faces, tree: node(d.body, 0) });
})()
