// Load js/i18n.js + js/data.js once per language in a fake browser context and dump what the static build needs.
const fs = require("fs"), vm = require("vm");
const src = [".work/src/i18n.js", ".work/src/data.js"].map((f) => fs.readFileSync(f, "utf8"));
function load(lang) {
  const ctx = { window: {}, location: { search: "" }, URLSearchParams,
    document: { documentElement: { lang }, addEventListener() {}, querySelector() { return null; }, querySelectorAll() { return []; } } };
  vm.createContext(ctx);
  src.forEach((s) => vm.runInContext(s, ctx));
  return ctx.window;
}
const keys = [...src[0].matchAll(/^\s+"([\w.]+)":\s*\[/gm)].map((m) => m[1]);
const w0 = load("vi");
const out = { langs: w0.I18N.langs, T: {}, P: w0.CGP.P, INC: w0.CGP.INC, NEWS: w0.CGP.NEWS, nights: {}, short: {} };
for (const l of out.langs) {
  const I = load(l).I18N;
  out.T[l] = {}; keys.forEach((k) => (out.T[l][k] = I.t(k)));
  out.nights[l] = {}; [3, 4, 5, 7].forEach((n) => (out.nights[l][n] = I.nights(n)));
  out.short[l] = {}; out.NEWS.forEach((n) => (out.short[l][n.date] = I.shortDate(new Date(n.date))));
}
fs.writeFileSync(".work/i18n.json", JSON.stringify(out));
console.log("keys", keys.length, "langs", out.langs.join(","));
