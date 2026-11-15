(() => {
  const pick = (e, ps) => { if (!e) return null; const cs = getComputedStyle(e); const o = {}; ps.forEach((p) => (o[p] = cs[p])); o.r = e.getBoundingClientRect().toJSON(); o.y = o.r.top + scrollY; return o; };
  const F = ["fontFamily","fontSize","fontWeight","lineHeight","color","letterSpacing","textTransform","marginTop","marginBottom","paddingTop","paddingBottom","backgroundColor","borderTop","borderBottom","width","height"];
  const q = (s) => document.querySelector(s);
  const out = {};
  out.banner = pick(q(".banner-page"), F.concat(["backgroundImage"]));
  out.h1 = pick(q(".banner-page h1"), F);
  const art = q(".btArticleContentHolder, .btArticleBody, article, .btContent");
  out.content = [...document.querySelectorAll(".btContent *")].filter((e) => e.children.length === 0 && e.textContent.trim() && e.offsetHeight).slice(0, 40).map((e) => [e.tagName, (e.className || "").toString().slice(0, 40), e.textContent.trim().slice(0, 50), JSON.stringify(pick(e, ["fontFamily","fontSize","fontWeight","lineHeight","color","letterSpacing","textTransform"])).slice(0, 330), Math.round(e.getBoundingClientRect().left), Math.round(e.getBoundingClientRect().top + scrollY), Math.round(e.getBoundingClientRect().width)]);
  out.imgs = [...document.querySelectorAll(".btContent img")].filter((i) => i.offsetHeight).slice(0, 20).map((i) => [i.currentSrc.slice(-60), Math.round(i.getBoundingClientRect().left), Math.round(i.getBoundingClientRect().top + scrollY), i.offsetWidth, i.offsetHeight]);
  out.blocks = [...document.querySelectorAll(".btContent *")].filter((e) => { const cs = getComputedStyle(e); return (cs.backgroundColor !== "rgba(0, 0, 0, 0)" || cs.borderBottomWidth !== "0px" || cs.borderTopWidth !== "0px") && e.offsetHeight > 2; }).slice(0, 40).map((e) => [e.tagName, (e.className || "").toString().slice(0, 40), Math.round(e.getBoundingClientRect().left), Math.round(e.getBoundingClientRect().top + scrollY), e.offsetWidth, e.offsetHeight, getComputedStyle(e).backgroundColor, getComputedStyle(e).borderTop, getComputedStyle(e).borderBottom]);
  return JSON.stringify(out, null, 1);
})()
